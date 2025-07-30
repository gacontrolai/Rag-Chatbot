from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from datetime import datetime
from typing import Optional, Dict, Any
from extensions.db import get_db
from models.user import User, UserPlan

class UserRepository:
    def __init__(self):
        self.collection_name = 'users'
    
    @property
    def collection(self):
        db = get_db()
        return db[self.collection_name]
    
    def create_user(self, email: str, password_hash: str, name: str) -> Optional[str]:
        """Create a new user and return the user ID"""
        try:
            user_doc = {
                'email': email.lower(),
                'password_hash': password_hash,
                'name': name,
                'plan': UserPlan.FREE,
                'workspaces': [],
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(user_doc)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        user = self.collection.find_one({'email': email.lower()})
        if user:
            user['id'] = str(user['_id'])
            del user['_id']
        return user
    
    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['id'] = str(user['_id'])
                del user['_id']
            return user
        except:
            return None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """Update user data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def add_workspace_to_user(self, user_id: str, workspace_id: str) -> bool:
        """Add workspace to user's workspace list"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$addToSet': {'workspaces': workspace_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def remove_workspace_from_user(self, user_id: str, workspace_id: str) -> bool:
        """Remove workspace from user's workspace list"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$pull': {'workspaces': workspace_id},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            return result.modified_count > 0
        except:
            return False
    
    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('email', unique=True) 