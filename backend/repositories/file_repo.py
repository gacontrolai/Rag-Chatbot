from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from extensions.db import get_db
from models.file import FileStatus, TextChunk

class FileRepository:
    def __init__(self):
        self.collection_name = 'files'
    
    @property
    def collection(self):
        db = get_db()
        return db[self.collection_name]
    
    def create_file(self, workspace_id: str, uploader_id: str, filename: str, 
                   mime_type: str, size: int, storage_url: str) -> Optional[str]:
        """Create a new file record and return the file ID"""
        try:
            file_doc = {
                'workspace_id': workspace_id,
                'uploader_id': uploader_id,
                'filename': filename,
                'mime_type': mime_type,
                'size': size,
                'storage_url': storage_url,
                'text_chunks': [],
                'status': FileStatus.UPLOADED,
                'error': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(file_doc)
            return str(result.inserted_id)
        except:
            return None
    
    def find_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Find file by ID"""
        try:
            file_doc = self.collection.find_one({'_id': ObjectId(file_id)})
            if file_doc:
                file_doc['id'] = str(file_doc['_id'])
                del file_doc['_id']
            return file_doc
        except:
            return None
    
    def find_by_filename(self, workspace_id: str, filename: str) -> Optional[Dict[str, Any]]:
        """Find file by filename in workspace"""
        try:
            file_doc = self.collection.find_one({
                'workspace_id': workspace_id,
                'filename': filename
            })
            if file_doc:
                file_doc['id'] = str(file_doc['_id'])
                del file_doc['_id']
            return file_doc
        except:
            return None
    
    def find_by_workspace(self, workspace_id: str, skip: int = 0, limit: int = 20, 
                         status: Optional[FileStatus] = None) -> List[Dict[str, Any]]:
        """Find files in a workspace"""
        try:
            query = {'workspace_id': workspace_id}
            if status:
                query['status'] = status
            
            cursor = self.collection.find(query).skip(skip).limit(limit).sort('updated_at', -1)
            
            files = []
            for file_doc in cursor:
                file_doc['id'] = str(file_doc['_id'])
                del file_doc['_id']
                files.append(file_doc)
            
            return files
        except:
            return []
    
    def update_file(self, file_id: str, update_data: Dict[str, Any]) -> bool:
        """Update file data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(file_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def update_status(self, file_id: str, status: FileStatus, error: str = None) -> bool:
        """Update file processing status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.utcnow()
            }
            if error:
                update_data['error'] = error
            
            result = self.collection.update_one(
                {'_id': ObjectId(file_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def add_text_chunks(self, file_id: str, chunks: List[TextChunk]) -> bool:
        """Add text chunks to file"""
        try:
            chunk_dicts = [chunk.dict() for chunk in chunks]
            result = self.collection.update_one(
                {'_id': ObjectId(file_id)},
                {
                    '$set': {
                        'text_chunks': chunk_dicts,
                        'status': FileStatus.READY,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """Delete file record"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(file_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def delete_by_workspace(self, workspace_id: str) -> int:
        """Delete all files in a workspace"""
        try:
            result = self.collection.delete_many({'workspace_id': workspace_id})
            return result.deleted_count
        except:
            return 0
    
    def get_workspace_storage_used(self, workspace_id: str) -> int:
        """Get total storage used by workspace"""
        try:
            pipeline = [
                {'$match': {'workspace_id': workspace_id}},
                {'$group': {'_id': None, 'total_size': {'$sum': '$size'}}}
            ]
            result = list(self.collection.aggregate(pipeline))
            return result[0]['total_size'] if result else 0
        except:
            return 0
    
    def get_chunks_with_embeddings(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all text chunks with embeddings from all files in workspace"""
        try:
            pipeline = [
                {'$match': {
                    'workspace_id': workspace_id,
                    'status': FileStatus.READY,
                    'text_chunks': {'$ne': []}
                }},
                {'$unwind': '$text_chunks'},
                {'$match': {'text_chunks.embedding': {'$ne': []}}},
                {'$project': {
                    'file_id': {'$toString': '$_id'},
                    'filename': '$filename',
                    'chunk_id': '$text_chunks.chunk_id',
                    'text': '$text_chunks.text',
                    'embedding': '$text_chunks.embedding',
                    'start_pos': '$text_chunks.start_pos',
                    'end_pos': '$text_chunks.end_pos'
                }}
            ]
            
            chunks = list(self.collection.aggregate(pipeline))
            return chunks
        except Exception as e:
            print(f"Error getting chunks with embeddings: {e}")
            return []
    
    def search_text_chunks(self, workspace_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Basic text search in file chunks (fallback for when embeddings unavailable)"""
        try:
            pipeline = [
                {'$match': {
                    'workspace_id': workspace_id,
                    'status': FileStatus.READY,
                    'text_chunks': {'$ne': []}
                }},
                {'$unwind': '$text_chunks'},
                {'$match': {
                    'text_chunks.text': {'$regex': query, '$options': 'i'}
                }},
                {'$project': {
                    'file_id': {'$toString': '$_id'},
                    'filename': '$filename',
                    'chunk_id': '$text_chunks.chunk_id',
                    'text': '$text_chunks.text',
                    'start_pos': '$text_chunks.start_pos',
                    'end_pos': '$text_chunks.end_pos',
                    'similarity': 0.5  # Default similarity for text search
                }},
                {'$limit': top_k}
            ]
            
            results = list(self.collection.aggregate(pipeline))
            return results
        except Exception as e:
            print(f"Error in text search: {e}")
            return []
    
    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('workspace_id')
        self.collection.create_index('status')
        self.collection.create_index([('workspace_id', 1), ('status', 1)])
        # For text search (placeholder for vector search)
        self.collection.create_index([('text_chunks.text', 'text')]) 