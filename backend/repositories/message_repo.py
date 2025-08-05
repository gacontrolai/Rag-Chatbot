from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any
from extensions.db import get_db
from models.message import MessageRole, MessageMetadata

class MessageRepository:
    def __init__(self):
        self.collection_name = 'messages'
    
    @property
    def collection(self):
        db = get_db()
        return db[self.collection_name]
    
    def create_message(self, thread_id: str, role: MessageRole, content: str, 
                      metadata: Optional[MessageMetadata] = None) -> Optional[str]:
        """Create a new message and return the message ID"""
        try:
            message_doc = {
                'thread_id': thread_id,
                'role': role,
                'content': content,
                'metadata': metadata.dict() if metadata else {},
                'created_at': datetime.utcnow()
            }
            
            result = self.collection.insert_one(message_doc)
            return str(result.inserted_id)
        except:
            return None
    
    def find_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Find message by ID"""
        try:
            message = self.collection.find_one({'_id': ObjectId(message_id)})
            if message:
                message['id'] = str(message['_id'])
                del message['_id']
            return message
        except:
            return None
    
    def find_by_thread(self, thread_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Find messages in a thread, ordered by creation time"""
        try:
            cursor = self.collection.find({
                'thread_id': thread_id
            }).skip(skip).limit(limit).sort('created_at', 1)  # Ascending order for chat
            
            messages = []
            for message in cursor:
                message['id'] = str(message['_id'])
                del message['_id']
                messages.append(message)
            
            return messages
        except:
            return []
    
    def get_recent_messages(self, thread_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent messages for context (most recent first)"""
        try:
            cursor = self.collection.find({
                'thread_id': thread_id
            }).limit(limit).sort('created_at', -1)
            
            messages = []
            for message in cursor:
                message['id'] = str(message['_id'])
                del message['_id']
                messages.append(message)
            
            # Reverse to get chronological order
            return list(reversed(messages))
        except:
            return []
    
    def count_by_thread(self, thread_id: str) -> int:
        """Count messages in a thread"""
        try:
            return self.collection.count_documents({'thread_id': thread_id})
        except:
            return 0
    
    def delete_by_thread(self, thread_id: str) -> int:
        """Delete all messages in a thread"""
        try:
            result = self.collection.delete_many({'thread_id': thread_id})
            return result.deleted_count
        except:
            return 0
    
    def delete_by_workspace(self, workspace_id: str) -> int:
        """Delete all messages in threads belonging to a workspace"""
        # This requires a join-like operation, which is complex in MongoDB
        # For now, we'll handle this at the service layer
        pass
    
    def create_indexes(self):
        """Create database indexes"""
        self.collection.create_index('thread_id')
        self.collection.create_index([('thread_id', 1), ('created_at', 1)]) 