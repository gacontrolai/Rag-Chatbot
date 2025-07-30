from typing import List, Optional
from repositories.workspace_repo import WorkspaceRepository
from repositories.user_repo import UserRepository
from models.workspace import WorkspaceCreate, WorkspaceResponse, WorkspaceUpdate
from utils.exceptions import ValidationError, PermissionError

class WorkspaceService:
    def __init__(self):
        self.workspace_repo = WorkspaceRepository()
        self.user_repo = UserRepository()
    
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
        
        # Get created workspace
        workspace = self.workspace_repo.find_by_id(workspace_id)
        
        return WorkspaceResponse(
            id=workspace['id'],
            name=workspace['name'],
            owner_id=workspace['owner_id'],
            member_ids=workspace['member_ids'],
            doc_count=workspace['doc_count'],
            storage_used=workspace['storage_used'],
            settings=workspace['settings'],
            created_at=workspace['created_at'],
            updated_at=workspace['updated_at']
        )
    
    def get_workspace(self, workspace_id: str, user_id: str) -> Optional[WorkspaceResponse]:
        """Get workspace by ID"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Check access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        return WorkspaceResponse(
            id=workspace['id'],
            name=workspace['name'],
            owner_id=workspace['owner_id'],
            member_ids=workspace['member_ids'],
            doc_count=workspace['doc_count'],
            storage_used=workspace['storage_used'],
            settings=workspace['settings'],
            created_at=workspace['created_at'],
            updated_at=workspace['updated_at']
        )
    
    def get_user_workspaces(self, user_id: str, skip: int = 0, limit: int = 20) -> List[WorkspaceResponse]:
        """Get workspaces for a user"""
        workspaces = self.workspace_repo.find_by_user(user_id, skip=skip, limit=limit)
        
        return [
            WorkspaceResponse(
                id=ws['id'],
                name=ws['name'],
                owner_id=ws['owner_id'],
                member_ids=ws['member_ids'],
                doc_count=ws['doc_count'],
                storage_used=ws['storage_used'],
                settings=ws['settings'],
                created_at=ws['created_at'],
                updated_at=ws['updated_at']
            )
            for ws in workspaces
        ]
    
    def update_workspace(self, workspace_id: str, user_id: str, update_data: WorkspaceUpdate) -> Optional[WorkspaceResponse]:
        """Update workspace (owner only)"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return None
        
        # Only owner can update
        if workspace['owner_id'] != user_id:
            raise PermissionError("Only workspace owner can update workspace")
        
        # Update workspace
        update_dict = {}
        if update_data.name:
            update_dict['name'] = update_data.name
        if update_data.settings:
            update_dict['settings'] = update_data.settings.dict()
        
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
        
        # Remove workspace reference from any threads that use it
        from repositories.thread_repo import ThreadRepository
        thread_repo = ThreadRepository()
        thread_repo.delete_by_workspace(workspace_id)
        
        # TODO: Delete associated files
        # For now, just delete the workspace
        success = self.workspace_repo.delete_workspace(workspace_id)
        
        if success:
            # Remove from user's workspace list
            self.user_repo.remove_workspace_from_user(user_id, workspace_id)
        
        return success
    
    def add_member(self, workspace_id: str, user_id: str, member_user_id: str) -> bool:
        """Add member to workspace (owner only)"""
        workspace = self.workspace_repo.find_by_id(workspace_id)
        if not workspace:
            return False
        
        # Only owner can add members
        if workspace['owner_id'] != user_id:
            raise PermissionError("Only workspace owner can add members")
        
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
        
        return self.workspace_repo.get_workspace_stats(workspace_id) 