from typing import List, Optional
from repositories.workspace_repo import WorkspaceRepository
from repositories.user_repo import UserRepository
from models.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from utils.exceptions import ValidationError, PermissionError
from services.vector_service import VectorService

class WorkspaceService:
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()
        self.user_repo = UserRepository()
        self.vector_service = VectorService()
    
    def create_workspace(self, user_id: str, workspace_data: WorkspaceCreate) -> WorkspaceResponse:
        """Create a new workspace for file management and RAG"""
        # Create workspace
        workspace_id = self.workspace_repo.create_workspace(
            name=workspace_data.name,
            owner_id=user_id
        )
        
        if not workspace_id:
            raise Exception("Failed to create workspace")
        
        # Add workspace to user's workspace list
        self.user_repo.add_workspace_to_user(user_id, workspace_id)
        
        # Return created workspace
        return self.get_workspace(workspace_id, user_id)
    
    def get_workspace(self, workspace_id: str, user_id: str) -> Optional[WorkspaceResponse]:
        """Get workspace details"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Check permission
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        return WorkspaceResponse(
            id=workspace['id'],
            name=workspace['name'],
            owner_id=workspace['owner_id'],
            member_ids=workspace.get('member_ids', []),
            doc_count=workspace.get('doc_count', 0),
            storage_used=workspace.get('storage_used', 0),
            settings=workspace.get('settings', {}),
            created_at=workspace['created_at'],
            updated_at=workspace['updated_at']
        )
    
    def get_user_workspaces(self, user_id: str, skip: int = 0, limit: int = 20) -> List[WorkspaceResponse]:
        """Get workspaces for user"""
        workspaces = self.workspace_repo.find_by_user(user_id, skip=skip, limit=limit)
        
        return [
            WorkspaceResponse(
                id=workspace['id'],
                name=workspace['name'],
                owner_id=workspace['owner_id'],
                member_ids=workspace.get('member_ids', []),
                doc_count=workspace.get('doc_count', 0),
                storage_used=workspace.get('storage_used', 0),
                settings=workspace.get('settings', {}),
                created_at=workspace['created_at'],
                updated_at=workspace['updated_at']
            )
            for workspace in workspaces
        ]
    
    def update_workspace(self, workspace_id: str, user_id: str, 
                        workspace_data: WorkspaceUpdate) -> Optional[WorkspaceResponse]:
        """Update workspace"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Only owner or members can update (depending on what's being updated)
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        # Only owner can update name
        if workspace_data.name and workspace['owner_id'] != user_id:
            raise PermissionError("Only owner can update workspace name")
        
        # Build update dictionary
        update_dict = {}
        if workspace_data.name:
            update_dict['name'] = workspace_data.name
        if workspace_data.settings is not None:
            update_dict['settings'] = workspace_data.settings
        
        # Update workspace
        if update_dict:
            self.workspace_repo.update_workspace(workspace_id, update_dict)
        
        # Return updated workspace
        return self.get_workspace(workspace_id, user_id)
    
    def delete_workspace(self, workspace_id: str, user_id: str) -> bool:
        """Delete workspace (owner only)"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        # Only owner can delete
        if workspace['owner_id'] != user_id:
            raise PermissionError("Only workspace owner can delete workspace")
        
        try:
            # Remove workspace reference from any threads that use it
            from repositories.thread_repo import ThreadRepository
            thread_repo = ThreadRepository()
            thread_repo.delete_by_workspace(workspace_id)
            
            # Delete all embeddings for this workspace from vector store
            self.vector_service.delete_embeddings_by_workspace(workspace_id)
            
            # Delete all files in the workspace
            from repositories.file_repo import FileRepository
            file_repo = FileRepository()
            files = file_repo.find_by_workspace(workspace_id, limit=1000)  # Get all files
            
            for file_doc in files:
                try:
                    # Delete from storage
                    from extensions.storage import storage_manager
                    storage_manager.delete_file(file_doc['storage_url'])
                except Exception as e:
                    print(f"Error deleting file {file_doc['filename']}: {e}")
            
            # Delete files from database
            file_repo.delete_by_workspace(workspace_id)
            
            # Delete the workspace
            success = self.workspace_repo.delete_workspace(workspace_id)
            
            if success:
                # Remove from user's workspace list
                self.user_repo.remove_workspace_from_user(user_id, workspace_id)
                
                # Remove from all members' workspace lists
                for member_id in workspace.get('member_ids', []):
                    if member_id != user_id:  # Owner already handled above
                        self.user_repo.remove_workspace_from_user(member_id, workspace_id)
            
            return success
            
        except Exception as e:
            print(f"Error deleting workspace: {e}")
            return False
    
    def add_member(self, workspace_id: str, user_id: str, member_user_id: str) -> bool:
        """Add member to workspace (owner only)"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        # Only owner can add members
        if workspace['owner_id'] != user_id:
            raise PermissionError("Only workspace owner can add members")
        
        # Check if user exists
        member_user = self.user_repo.find_by_id(member_user_id)
        if not member_user:
            raise ValidationError("User not found")
        
        # Add member to workspace
        success = self.workspace_repo.add_member(workspace_id, member_user_id)
        
        if success:
            # Add workspace to member's workspace list
            self.user_repo.add_workspace_to_user(member_user_id, workspace_id)
        
        return success
    
    def remove_member(self, workspace_id: str, user_id: str, member_user_id: str) -> bool:
        """Remove member from workspace (owner only)"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        # Only owner can remove members
        if workspace['owner_id'] != user_id:
            raise PermissionError("Only workspace owner can remove members")
        
        # Can't remove owner
        if member_user_id == workspace['owner_id']:
            raise ValidationError("Cannot remove workspace owner")
        
        # Remove member from workspace
        success = self.workspace_repo.remove_member(workspace_id, member_user_id)
        
        if success:
            # Remove workspace from member's workspace list
            self.user_repo.remove_workspace_from_user(member_user_id, workspace_id)
        
        return success
    
    def get_workspace_stats(self, workspace_id: str, user_id: str) -> Optional[dict]:
        """Get workspace statistics"""
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        stats = self.workspace_repo.get_workspace_stats(workspace_id)
        
        # Add vector store stats
        vector_stats = self.vector_service.get_stats()
        if stats:
            stats['vector_store'] = vector_stats
        
        return stats 