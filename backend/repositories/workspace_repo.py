from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from extensions.db import get_db
from models.workspace import WorkspaceSettings

class WorkspaceRepository:
    def __init__(self):
        self.collection_name = 'workspaces'
    
    @property
    def collection(self):
        db = get_db()
        return db[self.collection_name]
    
    def create_workspace(self, name: str, owner_id: str) -> Optional[str]:
        """Create a new workspace and return the workspace ID"""
        try:
            workspace_doc = {
                'name': name,
                'owner_id': owner_id,
                'member_ids': [owner_id],  # Owner is automatically a member
                'doc_count': 0,
                'storage_used': 0,
                'settings': WorkspaceSettings().dict(),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(workspace_doc)
            return str(result.inserted_id)
        except:
            return None
    
    def find_by_id(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Find workspace by ID"""
        try:
            workspace = self.collection.find_one({'_id': ObjectId(workspace_id)})
            if workspace:
                workspace['id'] = str(workspace['_id'])
                del workspace['_id']
            return workspace
        except:
            return None
    
    def find_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Find workspaces where user is owner or member"""
        try:
            cursor = self.collection.find({
                '$or': [
                    {'owner_id': user_id},
                    {'member_ids': user_id}
                ]
            }).skip(skip).limit(limit).sort('updated_at', -1)
            
            workspaces = []
            for workspace in cursor:
                workspace['id'] = str(workspace['_id'])
                del workspace['_id']
                workspaces.append(workspace)
            
            return workspaces
        except:
            return []
    
    def update_workspace(self, workspace_id: str, update_data: Dict[str, Any]) -> bool:
        """Update workspace data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(workspace_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_workspace(self, workspace_id: str) -> bool:
        """Delete workspace"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(workspace_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def add_member(self, workspace_id: str, user_id: str) -> bool:
        """Add member to workspace"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(workspace_id)},
                {
                    '$addToSet': {'member_ids': user_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def remove_member(self, workspace_id: str, user_id: str) -> bool:
        """Remove member from workspace"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(workspace_id)},
                {
                    '$pull': {'member_ids': user_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def is_member(self, workspace_id: str, user_id: str) -> bool:
        """Check if user is a member of workspace"""
        try:
            workspace = self.collection.find_one({
                '_id': ObjectId(workspace_id),
                '$or': [
                    {'owner_id': user_id},
                    {'member_ids': user_id}
                ]
            })
            return workspace is not None
        except:
            return False
    
    def increment_file_counters(self, workspace_id: str, doc_count_delta: int = 0, 
                               storage_delta: int = 0) -> bool:
        """Increment workspace file-related counters"""
        try:
            update_data = {'updated_at': datetime.utcnow()}
            if doc_count_delta != 0:
                update_data['doc_count'] = doc_count_delta
            if storage_delta != 0:
                update_data['storage_used'] = storage_delta
            
            result = self.collection.update_one(
                {'_id': ObjectId(workspace_id)},
                {'$inc': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def get_workspace_stats(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace statistics"""
        try:
            workspace = self.find_by_id(workspace_id)
            if workspace:
                return {
                    'doc_count': workspace.get('doc_count', 0),
                    'storage_used': workspace.get('storage_used', 0),
                    'member_count': len(workspace.get('member_ids', [])),
                    'settings': workspace.get('settings', {})
                }
            return None
        except:
            return None
    
    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('owner_id')
        self.collection.create_index('member_ids') 