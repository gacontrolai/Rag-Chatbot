from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from extensions.db import get_db
from models.thread import ThreadStatus

class ThreadRepository:
    def __init__(self):
        self.collection_name = 'threads'
    
    @property
    def collection(self):
        db = get_db()
        return db[self.collection_name]
    
    def create_thread(self, user_id: str, title: str = None, workspace_id: str = None) -> Optional[str]:
        """Create a new thread and return the thread ID"""
        try:
            if not title:
                title = f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
            
            thread_doc = {
                'user_id': user_id,
                'title': title,
                'workspace_id': workspace_id,  # Optional workspace reference
                'status': ThreadStatus.OPEN,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(thread_doc)
            return str(result.inserted_id)
        except:
            return None
    
    def find_by_id(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Find thread by ID"""
        try:
            thread = self.collection.find_one({'_id': ObjectId(thread_id)})
            if thread:
                thread['id'] = str(thread['_id'])
                del thread['_id']
            return thread
        except:
            return None
    
    def find_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Find threads created by user"""
        try:
            cursor = self.collection.find({
                'user_id': user_id
            }).skip(skip).limit(limit).sort('updated_at', -1)
            
            threads = []
            for thread in cursor:
                thread['id'] = str(thread['_id'])
                del thread['_id']
                threads.append(thread)
            
            return threads
        except:
            return []
    
    def find_by_workspace(self, workspace_id: str, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Find threads that reference a specific workspace"""
        try:
            cursor = self.collection.find({
                'workspace_id': workspace_id
            }).skip(skip).limit(limit).sort('updated_at', -1)
            
            threads = []
            for thread in cursor:
                thread['id'] = str(thread['_id'])
                del thread['_id']
                threads.append(thread)
            
            return threads
        except:
            return []
    
    def find_user_threads_with_workspace(self, user_id: str, workspace_id: str, 
                                        skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """Find user's threads that reference a specific workspace"""
        try:
            cursor = self.collection.find({
                'user_id': user_id,
                'workspace_id': workspace_id
            }).skip(skip).limit(limit).sort('updated_at', -1)
            
            threads = []
            for thread in cursor:
                thread['id'] = str(thread['_id'])
                del thread['_id']
                threads.append(thread)
            
            return threads
        except:
            return []
    
    def update_thread(self, thread_id: str, update_data: Dict[str, Any]) -> bool:
        """Update thread data"""
        try:
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {'_id': ObjectId(thread_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except:
            return False
    
    def delete_thread(self, thread_id: str) -> bool:
        """Delete thread"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(thread_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def delete_by_workspace(self, workspace_id: str) -> int:
        """Remove workspace reference from threads (don't delete threads)"""
        try:
            result = self.collection.update_many(
                {'workspace_id': workspace_id},
                {'$unset': {'workspace_id': ""}, '$set': {'updated_at': datetime.utcnow()}}
            )
            return result.modified_count
        except:
            return 0
    
    def count_by_user(self, user_id: str) -> int:
        """Count threads created by user"""
        try:
            return self.collection.count_documents({'user_id': user_id})
        except:
            return 0
    
    def count_by_workspace(self, workspace_id: str) -> int:
        """Count threads referencing a workspace"""
        try:
            return self.collection.count_documents({'workspace_id': workspace_id})
        except:
            return 0
    
    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('user_id')
        self.collection.create_index('workspace_id', sparse=True)  # Sparse since it's optional
        self.collection.create_index([('user_id', 1), ('updated_at', -1)])
        self.collection.create_index([('workspace_id', 1), ('updated_at', -1)], sparse=True) 