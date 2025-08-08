from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from repositories.file_repo import FileRepository
from repositories.workspace_repo import WorkspaceRepository
from models.file import FileResponse, FileUpload, FileStatus
from extensions.storage import storage_manager
from utils.exceptions import ValidationError, PermissionError
from utils.content_extractor import ContentExtractor
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

class FileService:
    def __init__(self):
        self.file_repo = FileRepository()
        self.workspace_repo = WorkspaceRepository()
        self.embedding_service = EmbeddingService()
        self.vector_service = VectorService()
    
    def upload_file(self, workspace_id: str, user_id: str, file: FileStorage, 
                   file_data: Optional[FileUpload] = None) -> FileResponse:
        """Upload file to workspace with content extraction and embedding"""
        # Verify workspace access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        # Validate file
        if not file or not file.filename:
            raise ValidationError("No file provided")
        
        # Check if file format is supported
        if not ContentExtractor.is_supported_format(file.filename):
            raise ValidationError(f"Unsupported file format. Supported formats: .txt, .csv, .docx")
        
        # Check for duplicate files in workspace
        existing_file = self.file_repo.find_by_filename(workspace_id, file.filename)
        if existing_file:
            raise ValidationError(f"File '{file.filename}' already exists in this workspace")
        
        # Check file size (basic validation)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            raise ValidationError("File too large (max 50MB)")
        
        try:
            # Extract content from file
            content_data = ContentExtractor.extract_content(file)
            
            # Reset file pointer for storage
            file.seek(0)
            
            # Save file using storage manager
            storage_url = storage_manager.save_file(file, workspace_id, file.filename)
            
            # Create file record with processing status
            file_id = self.file_repo.create_file(
                workspace_id=workspace_id,
                uploader_id=user_id,
                filename=file.filename,
                mime_type=file.mimetype or 'application/octet-stream',
                size=file_size,
                storage_url=storage_url
            )
            
            if not file_id:
                raise Exception("Failed to create file record")
            
            # Update file status to processing
            self.file_repo.update_status(file_id, FileStatus.PROCESSING)
            
            try:
                # Create embeddings for text chunks
                text_chunks = []
                if content_data['chunks'] and self.embedding_service.is_available():
                    chunk_texts = [chunk['text'] for chunk in content_data['chunks']]
                    embeddings = self.embedding_service.create_embeddings(chunk_texts)
                    
                    # Create text chunks with embeddings
                    for i, chunk in enumerate(content_data['chunks']):
                        embedding = embeddings[i] if i < len(embeddings) else []
                        text_chunks.append({
                            'chunk_id': chunk['chunk_id'],
                            'text': chunk['text'],
                            'embedding': embedding,
                            'start_pos': chunk['start_pos'],
                            'end_pos': chunk['end_pos'],
                            'char_count': chunk['char_count'],
                            'filename': file.filename
                        })
                
                # Store embeddings using vector service
                if text_chunks:
                    vector_success = self.vector_service.store_embeddings(
                        workspace_id, file_id, text_chunks
                    )
                    
                    if not vector_success:
                        print(f"Warning: Failed to store embeddings in vector store for file {file.filename}")
                        # Still continue with MongoDB storage as fallback
                        self.file_repo.add_text_chunks(file_id, text_chunks)
                
                # Update file status to ready
                self.file_repo.update_status(file_id, FileStatus.READY)
                
            except Exception as e:
                # Update file status to failed with error message
                error_msg = f"Content processing failed: {str(e)}"
                self.file_repo.update_status(file_id, FileStatus.FAILED, error_msg)
                print(f"File processing error for {file.filename}: {e}")
            
            # Update workspace counters
            self.workspace_repo.increment_file_counters(
                workspace_id, 
                doc_count_delta=1, 
                storage_delta=file_size
            )
            
            # Get created file
            file_doc = self.file_repo.find_by_id(file_id)
            
            return FileResponse(
                id=file_doc['id'],
                workspace_id=file_doc['workspace_id'],
                uploader_id=file_doc['uploader_id'],
                filename=file_doc['filename'],
                mime_type=file_doc['mime_type'],
                size=file_doc['size'],
                storage_url=file_doc['storage_url'],
                status=file_doc['status'],
                error=file_doc.get('error'),
                created_at=file_doc['created_at'],
                updated_at=file_doc['updated_at']
            )
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def search_files(self, workspace_id: str, user_id: str, query: str, 
                    top_k: int = 5) -> List[Dict[str, Any]]:
        """Search files in workspace using semantic similarity"""
        # Verify workspace access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        if not query.strip():
            return []
        
        if not self.embedding_service.is_available():
            # Fallback to basic text search
            return self._basic_text_search(workspace_id, query, top_k)
        
        try:
            # Create embedding for search query
            query_embedding = self.embedding_service.create_single_embedding(query)
            
            if not query_embedding:
                return self._basic_text_search(workspace_id, query, top_k)
            
            # Use vector service for search
            similar_chunks = self.vector_service.search_similar(
                query_embedding, workspace_id, top_k
            )
            
            return similar_chunks
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return self._basic_text_search(workspace_id, query, top_k)
    
    def _basic_text_search(self, workspace_id: str, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Fallback basic text search"""
        try:
            return self.file_repo.search_text_chunks(workspace_id, query, top_k)
        except Exception as e:
            print(f"Error in basic text search: {e}")
            return []
    
    def get_workspace_files(self, workspace_id: str, user_id: str, 
                           skip: int = 0, limit: int = 20) -> List[FileResponse]:
        """Get files in workspace"""
        # Verify workspace access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        files = self.file_repo.find_by_workspace(workspace_id, skip=skip, limit=limit)
        
        return [
            FileResponse(
                id=file_doc['id'],
                workspace_id=file_doc['workspace_id'],
                uploader_id=file_doc['uploader_id'],
                filename=file_doc['filename'],
                mime_type=file_doc['mime_type'],
                size=file_doc['size'],
                storage_url=file_doc['storage_url'],
                status=file_doc['status'],
                error=file_doc.get('error'),
                created_at=file_doc['created_at'],
                updated_at=file_doc['updated_at']
            )
            for file_doc in files
        ]
    
    def get_file_details(self, file_id: str, user_id: str) -> Optional[FileResponse]:
        """Get detailed file information"""
        file_doc = self.file_repo.find_by_id(file_id)
        if not file_doc:
            return None
        
        # Check permission
        if not self.workspace_repo.is_member(file_doc['workspace_id'], user_id):
            raise PermissionError("Access denied to workspace")
        
        return FileResponse(
            id=file_doc['id'],
            workspace_id=file_doc['workspace_id'],
            uploader_id=file_doc['uploader_id'],
            filename=file_doc['filename'],
            mime_type=file_doc['mime_type'],
            size=file_doc['size'],
            storage_url=file_doc['storage_url'],
            status=file_doc['status'],
            error=file_doc.get('error'),
            created_at=file_doc['created_at'],
            updated_at=file_doc['updated_at']
        )
    
    def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete file"""
        file_doc = self.file_repo.find_by_id(file_id)
        if not file_doc:
            return False
        
        # Check permission (uploader or workspace owner)
        if file_doc['uploader_id'] != user_id:
            workspace = self.workspace_repo.find_by_id(file_doc['workspace_id'])
            if not workspace or workspace['owner_id'] != user_id:
                raise PermissionError("Permission denied")
        
        try:
            # Delete embeddings from vector store
            self.vector_service.delete_embeddings_by_file(
                file_id, file_doc['workspace_id']
            )
            
            # Delete from storage
            storage_manager.delete_file(file_doc['storage_url'])
            
            # Delete from database
            success = self.file_repo.delete_file(file_id)
            
            if success:
                # Update workspace counters
                self.workspace_repo.increment_file_counters(
                    file_doc['workspace_id'],
                    doc_count_delta=-1,
                    storage_delta=-file_doc['size']
                )
            
            return success
            
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_vector_stats(self) -> Dict[str, Any]:
        """Get vector service statistics"""
        return self.vector_service.get_stats() 