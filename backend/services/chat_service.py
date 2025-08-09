import time
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from repositories.thread_repo import ThreadRepository
from repositories.message_repo import MessageRepository
from repositories.workspace_repo import WorkspaceRepository
from repositories.file_repo import FileRepository
from models.message import MessageCreate, MessageResponse, MessageRole, MessageMetadata
from models.thread import ThreadCreate, ThreadResponse
from utils.exceptions import ValidationError, PermissionError
from services.rag_service import RAGService
from prompts.prompt_manager import PromptManager

# LangChain imports
try:
    from langchain_openai import ChatOpenAI
    from langchain.schema import SystemMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("LangChain not available, using fallback response system")

class ChatService:
    def __init__(self):
        self.thread_repo = ThreadRepository()
        self.message_repo = MessageRepository()
        self.workspace_repo = WorkspaceRepository()
        self.file_repo = FileRepository()
        self.rag_service = RAGService()
        self.prompt_manager = PromptManager()
        
        # Initialize LangChain components if available
        self.llm = None
        if LANGCHAIN_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            try:
                self.llm = ChatOpenAI(
                    model_name=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                    base_url=os.getenv('OPENAI_BASE_URL'),
                    temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
                    openai_api_key=os.getenv('OPENAI_API_KEY'),
                    max_tokens=1000
                )
                print("LangChain ChatOpenAI initialized successfully")
            except Exception as e:
                print(f"Failed to initialize LangChain ChatOpenAI: {e}")
                self.llm = None
    
    def create_thread(self, user_id: str, thread_data: ThreadCreate) -> ThreadResponse:
        """Create a new independent chat thread"""
        # Verify workspace access if workspace_id is provided
        if thread_data.workspace_id:
            if not self.workspace_repo.is_member(thread_data.workspace_id, user_id):
                raise PermissionError("Access denied to workspace")
        
        # Create thread (independent of workspace)
        thread_id = self.thread_repo.create_thread(
            user_id=user_id,
            title=thread_data.title,
            workspace_id=thread_data.workspace_id  # Optional workspace reference
        )
        
        if not thread_id:
            raise Exception("Failed to create thread")
        
        # Get created thread
        thread = self.thread_repo.find_by_id(thread_id)
        
        return ThreadResponse(
            id=thread['id'],
            user_id=thread['user_id'],
            title=thread['title'],
            workspace_id=thread.get('workspace_id'),
            status=thread['status'],
            created_at=thread['created_at'],
            updated_at=thread['updated_at']
        )
    
    def send_message(self, thread_id: str, user_id: str, message_data: MessageCreate) -> MessageResponse:
        """Send a message and get AI response"""
        start_time = time.time()
        
        # Verify thread access and ownership
        thread = self.thread_repo.find_by_id(thread_id)
        if not thread:
            raise ValidationError("Thread not found")
        
        # Check if user owns the thread
        if thread['user_id'] != user_id:
            raise PermissionError("Access denied to thread")
        
        # Verify workspace access if thread references a workspace
        workspace_id = thread.get('workspace_id')
        if workspace_id and not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to referenced workspace")
        
        # Prepare user content and optionally attach RAG context BEFORE saving the user message
        user_content = message_data.content.strip()
        context_chunks: List[Dict[str, Any]] = []
        if message_data.use_rag and workspace_id:
            context_chunks = self.rag_service.search_context(
                workspace_id=workspace_id,
                query=user_content,
                top_k=message_data.top_k
            )
        
        # Build the exact user message that will be sent to the LLM (includes RAG context text)
        prepared_user_message = self._build_user_message_with_context(
            user_content=user_content,
            context_chunks=context_chunks,
            workspace_id=workspace_id
        )
        
        # # Save user message (store the real message that is sent to AI)
        # user_message_id = self.message_repo.create_message(
        #     thread_id=thread_id,
        #     role=MessageRole.USER,
        #     content=prepared_user_message
        # )
        
        # if not user_message_id:
        #     raise Exception("Failed to save user message")
        
        # # Get user message for response
        # user_message = self.message_repo.find_by_id(user_message_id)
        # user_response = MessageResponse(
        #     id=user_message['id'],
        #     thread_id=user_message['thread_id'],
        #     role=user_message['role'],
        #     content=user_message['content'],
        #     metadata=user_message.get('metadata'),
        #     created_at=user_message['created_at']
        # )
        
        # Generate AI response using the prepared message and precomputed context
        try:
            ai_response_content = self._generate_ai_response(
                thread=thread,
                message_data=message_data,
                user_content=user_content,
                context_chunks=context_chunks,
                prepared_user_message=prepared_user_message
            )
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Create AI response metadata
            ai_metadata = MessageMetadata(
                tokens=len(ai_response_content.split()),  # Simple token estimate
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo') if self.llm else "pattern-based",
                latency_ms=latency_ms
            )

        # Save user message (store the real message that is sent to AI)
            user_message_id = self.message_repo.create_message(
                thread_id=thread_id,
                role=MessageRole.USER,
                content=prepared_user_message
            )
            if not user_message_id:
                raise Exception("Failed to save user message")
            
            # Save AI message
            ai_message_id = self.message_repo.create_message(
                thread_id=thread_id,
                role=MessageRole.ASSISTANT,
                content=ai_response_content,
                metadata=ai_metadata
            )
            
            if ai_message_id:
                # Get AI message for response
                ai_message = self.message_repo.find_by_id(ai_message_id)
                
                # Update thread timestamp
                self.thread_repo.update_thread(thread_id, {})
                
                return MessageResponse(
                    id=ai_message['id'],
                    thread_id=ai_message['thread_id'],
                    role=ai_message['role'],
                    content=ai_message['content'],
                    metadata=ai_message.get('metadata'),
                    created_at=ai_message['created_at']
                )
        except Exception as e:
            print(f"Error generating AI response: {e}")
            # Return user message if AI fails
            pass
        
        # return user_response
    
    def _build_user_message_with_context(self, user_content: str, context_chunks: List[Dict[str, Any]],
                                         workspace_id: Optional[str]) -> str:
        """Construct the exact user message (with RAG context) that is sent to the LLM."""
        return self.prompt_manager.format_user_context_message(
            user_message=user_content,
            context_chunks=context_chunks,
            workspace_id=workspace_id
        )
    
    def _generate_ai_response(self, thread: Dict[str, Any], message_data: MessageCreate, user_content: str,
                              context_chunks: Optional[List[Dict[str, Any]]] = None,
                              prepared_user_message: Optional[str] = None) -> str:
        """Generate AI response using LangChain and OpenAI or fallback to basic response"""
        try:
            # Get conversation context (exclude the current just-saved message to avoid duplication)
            recent_messages = self.message_repo.get_recent_messages(thread['id'], limit=10)
            
            # Use LangChain if available
            if self.llm:
                return self._generate_langchain_response(
                    user_content=user_content,
                    context_chunks=context_chunks or [],
                    recent_messages=recent_messages,
                    temperature=message_data.temperature,
                    workspace_id=thread.get('workspace_id'),
                    prepared_user_message=prepared_user_message
                )
            else:
                # Fallback to basic response
                return self._create_basic_response(user_content, context_chunks or [], recent_messages)
            
        except Exception as e:
            print(f"Error in _generate_ai_response: {e}")
            # Fallback response
            return f"I understand you're asking about: '{user_content[:100]}{'...' if len(user_content) > 100 else ''}'. I'm processing your request and will provide a detailed response. Due to a temporary issue, I'm providing this placeholder response."
    
    def _generate_langchain_response(self, user_content: str, context_chunks: List[Dict], 
                                     recent_messages: List[Dict], temperature: float, workspace_id: Optional[str],
                                     prepared_user_message: Optional[str] = None) -> str:
        """Generate response using LangChain and OpenAI"""
        try:
            # Prepare messages for LangChain
            messages = [SystemMessage(content=self.prompt_manager.get_system_prompt())]
            
            # Add conversation history (limit to prevent token overflow)
            for msg in recent_messages[-8:]:  # Last 8 messages to keep context manageable
                if msg['role'] == MessageRole.USER:
                    messages.append(HumanMessage(content=msg['content']))
                elif msg['role'] == MessageRole.ASSISTANT:
                    messages.append(AIMessage(content=msg['content']))
            
            # Create the user message with context (use pre-built to ensure exact match with stored content)
            if prepared_user_message is None:
                prepared_user_message = self._build_user_message_with_context(
                    user_content=user_content,
                    context_chunks=context_chunks,
                    workspace_id=workspace_id
                )
            messages.append(HumanMessage(content=prepared_user_message))
            
            # Update LLM temperature for this specific request
            self.llm.temperature = temperature
            
            # Generate response
            response = self.llm.invoke(messages)
            
            return response.content.strip()
            
        except Exception as e:
            print(f"Error in LangChain response generation: {e}")
            # Fallback to basic response
            return self._create_basic_response(user_content, context_chunks, recent_messages)
    
    def _create_basic_response(self, user_content: str, context_chunks: List[Dict], recent_messages: List[Dict]) -> str:
        """Create a basic AI response (fallback for when LangChain is not available)"""
        # This is a simple pattern-based response system
        # In production, this would call OpenAI API
        
        user_lower = user_content.lower()
        
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'greeting']):
            return "Hello! How can I help you today? Feel free to ask me any questions or let me know what you'd like to discuss."
        
        elif any(word in user_lower for word in ['help', 'assist', 'support']):
            return "I'm here to help! You can ask me questions, request information, or discuss any topic you're interested in. What would you like assistance with?"
        
        elif '?' in user_content:
            # Questions get more detailed responses
            base_response = f"That's an interesting question about {user_content[:50]}{'...' if len(user_content) > 50 else ''}. "
            
            if context_chunks:
                base_response += f"Based on the documents in the referenced workspace, I found {len(context_chunks)} relevant pieces of information that might help answer your question. "
            
            base_response += "Let me provide you with a comprehensive response based on the available information."
            
            # Add context if available
            if context_chunks:
                base_response += "\n\nRelevant information from your documents:\n"
                for i, chunk in enumerate(context_chunks[:2], 1):
                    base_response += f"\n{i}. {chunk['text'][:200]}{'...' if len(chunk['text']) > 200 else ''}"
            
            return base_response
        
        else:
            # General statements
            response = f"I understand you're mentioning: '{user_content[:100]}{'...' if len(user_content) > 100 else ''}'. "
            
            if context_chunks:
                response += f"I found {len(context_chunks)} related documents in the referenced workspace that might provide additional context. "
            
            response += "Could you please provide more details or ask a specific question so I can give you a more targeted response?"
            
            return response
    
    def get_thread_messages(self, thread_id: str, user_id: str, skip: int = 0, limit: int = 50) -> List[MessageResponse]:
        """Get messages in a thread"""
        # Verify thread access and ownership
        thread = self.thread_repo.find_by_id(thread_id)
        if not thread:
            raise ValidationError("Thread not found")
        
        if thread['user_id'] != user_id:
            raise PermissionError("Access denied to thread")
        
        # Get messages
        messages = self.message_repo.find_by_thread(thread_id, skip=skip, limit=limit)
        
        return [
            MessageResponse(
                id=msg['id'],
                thread_id=msg['thread_id'],
                role=msg['role'],
                content=msg['content'],
                metadata=msg.get('metadata'),
                created_at=msg['created_at']
            )
            for msg in messages
        ]
    
    def get_thread(self, thread_id: str, user_id: str) -> Optional[ThreadResponse]:
        """Get thread by ID"""
        thread = self.thread_repo.find_by_id(thread_id)
        if not thread:
            return None
        
        # Verify ownership
        if thread['user_id'] != user_id:
            raise PermissionError("Access denied to thread")
        
        return ThreadResponse(
            id=thread['id'],
            user_id=thread['user_id'],
            title=thread['title'],
            workspace_id=thread.get('workspace_id'),
            status=thread['status'],
            created_at=thread['created_at'],
            updated_at=thread['updated_at']
        )
    
    def get_user_threads(self, user_id: str, skip: int = 0, limit: int = 20) -> List[ThreadResponse]:
        """Get threads created by user"""
        threads = self.thread_repo.find_by_user(user_id, skip=skip, limit=limit)
        
        return [
            ThreadResponse(
                id=thread['id'],
                user_id=thread['user_id'],
                title=thread['title'],
                workspace_id=thread.get('workspace_id'),
                status=thread['status'],
                created_at=thread['created_at'],
                updated_at=thread['updated_at']
            )
            for thread in threads
        ]
    
    def get_workspace_threads(self, workspace_id: str, user_id: str, skip: int = 0, limit: int = 20) -> List[ThreadResponse]:
        """Get threads that reference a specific workspace"""
        # Verify workspace access
        if not self.workspace_repo.is_member(workspace_id, user_id):
            raise PermissionError("Access denied to workspace")
        
        threads = self.thread_repo.find_by_workspace(workspace_id, skip=skip, limit=limit)
        
        return [
            ThreadResponse(
                id=thread['id'],
                user_id=thread['user_id'],
                title=thread['title'],
                workspace_id=thread.get('workspace_id'),
                status=thread['status'],
                created_at=thread['created_at'],
                updated_at=thread['updated_at']
            )
            for thread in threads
        ]
    
    def update_thread(self, thread_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[ThreadResponse]:
        """Update thread (title, workspace reference, status)"""
        thread = self.thread_repo.find_by_id(thread_id)
        if not thread:
            return None
        
        # Verify ownership
        if thread['user_id'] != user_id:
            raise PermissionError("Access denied to thread")
        
        # If updating workspace_id, verify user has access
        if 'workspace_id' in update_data and update_data['workspace_id']:
            if not self.workspace_repo.is_member(update_data['workspace_id'], user_id):
                raise PermissionError("Access denied to workspace")
        
        # Update thread
        if self.thread_repo.update_thread(thread_id, update_data):
            return self.get_thread(thread_id, user_id)
        
        return None
    
    def delete_thread(self, thread_id: str, user_id: str) -> bool:
        """Delete thread"""
        thread = self.thread_repo.find_by_id(thread_id)
        if not thread:
            return False
        
        # Verify ownership
        if thread['user_id'] != user_id:
            raise PermissionError("Access denied to thread")
        
        # Delete messages first
        self.message_repo.delete_by_thread(thread_id)
        
        # Delete thread
        return self.thread_repo.delete_thread(thread_id) 