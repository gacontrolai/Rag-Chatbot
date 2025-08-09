# Prompts Module

This module manages all system prompts and templates used by the chat service. It provides a centralized way to manage, update, and customize prompts without modifying the core application logic.

## Structure

```
prompts/
├── __init__.py          # Module initialization
├── prompt_manager.py    # Core prompt management logic
├── prompts_config.py    # Configuration file with all prompts
└── README.md           # This documentation
```

## Key Components

### PromptManager
The main class that handles prompt management operations:
- Loading prompts from configuration
- Retrieving specific prompts by type or name
- Updating prompts at runtime
- Formatting user messages with RAG context

### PromptType Enum
Defines standard prompt types:
- `SYSTEM`: Main system prompt for the AI assistant
- `USER_CONTEXT`: Template for user messages with RAG context
- `FALLBACK`: Fallback prompt when LLM is unavailable
- `SUMMARIZATION`: For content summarization tasks
- `CODE_REVIEW`: For code review tasks
- `EXPLANATION`: For explaining concepts

### Configuration File
`prompts_config.py` contains all prompt definitions and can be easily modified without touching the core logic.

## Usage

### Basic Usage
```python
from prompts.prompt_manager import PromptManager, PromptType

# Initialize the prompt manager
prompt_manager = PromptManager()

# Get the system prompt
system_prompt = prompt_manager.get_system_prompt()

# Get a specific prompt by type
fallback_prompt = prompt_manager.get_prompt(PromptType.FALLBACK)

# Get a prompt by name
custom_prompt = prompt_manager.get_prompt_by_name("code_review")
```

### Updating Prompts
```python
# Update a prompt by type
prompt_manager.update_prompt(PromptType.SYSTEM, "New system prompt content")

# Update a prompt by name
prompt_manager.update_prompt_by_name("summarization", "New summarization prompt")

# Add a custom prompt
prompt_manager.add_custom_prompt("translation", "Please translate the following text:")
```

### Formatting User Messages with Context
```python
# Format a user message with RAG context
formatted_message = prompt_manager.format_user_context_message(
    user_message="What is machine learning?",
    context_chunks=[...],  # List of context chunks
    workspace_id="workspace_123"
)
```

### Managing Prompts
```python
# Get all available prompts
all_prompts = prompt_manager.get_available_prompts()

# List all prompt names
prompt_names = prompt_manager.list_prompt_names()

# Reload prompts from configuration
prompt_manager.reload_prompts()
```

## Adding New Prompts

### Method 1: Configuration File (Recommended)
Add new prompts to `prompts_config.py`:

```python
# In prompts_config.py
NEW_PROMPT = "Your new prompt content here..."

PROMPTS_REGISTRY = {
    # ... existing prompts
    "new_prompt_name": NEW_PROMPT,
}
```

### Method 2: Runtime Addition
```python
# Add prompt at runtime
prompt_manager.add_custom_prompt("dynamic_prompt", "Dynamic prompt content")
```

### Method 3: Extending PromptType Enum
For standard prompt types, add to the enum:

```python
class PromptType(Enum):
    # ... existing types
    NEW_TYPE = "new_type"
```

## Integration with Chat Service

The chat service automatically uses the prompt manager:

```python
# In chat_service.py
from prompts.prompt_manager import PromptManager

class ChatService:
    def __init__(self):
        # ... other initializations
        self.prompt_manager = PromptManager()
    
    def _generate_langchain_response(self, ...):
        # Uses the system prompt from prompt manager
        messages = [SystemMessage(content=self.prompt_manager.get_system_prompt())]
        # ... rest of the logic
```

## Best Practices

1. **Use Configuration File**: Define all standard prompts in `prompts_config.py` for easy modification.

2. **Version Control**: Keep prompt changes in version control to track modifications over time.

3. **Testing**: Test prompt changes thoroughly before deploying to production.

4. **Documentation**: Document the purpose and expected behavior of each prompt.

5. **Naming Convention**: Use descriptive names for prompts (e.g., `code_review_detailed`, `summary_brief`).

6. **Validation**: Consider adding prompt validation to ensure required elements are present.

## Future Enhancements

- **Prompt Templates**: Support for parameterized prompts with variables
- **A/B Testing**: Framework for testing different prompt variations
- **Prompt Analytics**: Tracking prompt performance and effectiveness
- **External Storage**: Option to store prompts in database or external files
- **Role-based Prompts**: Different prompts based on user roles or contexts 