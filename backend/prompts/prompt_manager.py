"""
Prompt Manager for handling system prompts and templates
"""
from typing import Dict, Optional
from enum import Enum
from .prompts_config import PROMPTS_REGISTRY, SYSTEM_PROMPT, USER_CONTEXT_TEMPLATE, FALLBACK_PROMPT

class PromptType(Enum):
    """Types of prompts available in the system"""
    SYSTEM = "system"
    USER_CONTEXT = "user_context"
    FALLBACK = "fallback"
    SUMMARIZATION = "summarization"
    CODE_REVIEW = "code_review"
    EXPLANATION = "explanation"

class PromptManager:
    """Manages system prompts and templates for the chat service"""
    
    def __init__(self):
        self._prompts = self._load_prompts_from_config()
    
    def _load_prompts_from_config(self) -> Dict[str, str]:
        """Load all prompts from the configuration file"""
        return PROMPTS_REGISTRY.copy()
    
    def _get_system_prompt(self) -> str:
        """Main system prompt for the AI assistant"""
        return SYSTEM_PROMPT
    
    def _get_user_context_prompt(self) -> str:
        """Template for adding RAG context to user messages"""
        return USER_CONTEXT_TEMPLATE
    
    def _get_fallback_prompt(self) -> str:
        """Fallback prompt when LLM is unavailable"""
        return FALLBACK_PROMPT
    
    def get_prompt(self, prompt_type: PromptType) -> str:
        """Get a specific prompt by type"""
        return self._prompts.get(prompt_type.value, "")
    
    def get_prompt_by_name(self, prompt_name: str) -> str:
        """Get a prompt by its string name"""
        return self._prompts.get(prompt_name, "")
    
    def get_system_prompt(self) -> str:
        """Get the main system prompt"""
        return self.get_prompt(PromptType.SYSTEM)
    
    def update_prompt(self, prompt_type: PromptType, new_prompt: str) -> bool:
        """Update a specific prompt"""
        try:
            self._prompts[prompt_type.value] = new_prompt
            return True
        except Exception as e:
            print(f"Error updating prompt {prompt_type.value}: {e}")
            return False
    
    def update_prompt_by_name(self, prompt_name: str, new_prompt: str) -> bool:
        """Update a prompt by its string name"""
        try:
            self._prompts[prompt_name] = new_prompt
            return True
        except Exception as e:
            print(f"Error updating prompt {prompt_name}: {e}")
            return False
    
    def format_user_context_message(self, user_message: str, context_chunks: list, 
                                   workspace_id: Optional[str] = None) -> str:
        """Format user message with RAG context using the configured template"""
        if context_chunks:
            # Build the context content from chunks
            context_content = ""
            for i, chunk in enumerate(context_chunks, 1):
                snippet = chunk['text']
                context_content += f"\n##{i}.Chunk {chunk['filename']}({chunk['start_pos']}-{chunk['end_pos']}):\n{snippet}\n"
            
            # Use the template to format the message
            template = self.get_prompt_by_name("user_context")
            return template.format(
                user_message=user_message,
                context_content=context_content
            ).strip()
            
        elif workspace_id:
            # No relevant documents found case
            no_docs_message = "\n\n(No relevant documents found in the workspace for this query)\n"
            return f"{no_docs_message}\nUser: {user_message}"
        else:
            # No workspace context at all
            return f"User: {user_message}"
    
    def get_available_prompts(self) -> Dict[str, str]:
        """Get all available prompts"""
        return self._prompts.copy()
    
    def reload_prompts(self) -> None:
        """Reload all prompts from configuration (useful for dynamic updates)"""
        self._prompts = self._load_prompts_from_config()
    
    def add_custom_prompt(self, prompt_name: str, prompt_content: str) -> bool:
        """Add a custom prompt at runtime"""
        try:
            self._prompts[prompt_name] = prompt_content
            return True
        except Exception as e:
            print(f"Error adding custom prompt {prompt_name}: {e}")
            return False
    
    def list_prompt_names(self) -> list:
        """Get a list of all available prompt names"""
        return list(self._prompts.keys()) 