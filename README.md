# AI Chatbot API

A comprehensive Flask-based AI chatbot application with independent chat threads, workspace-based file management, advanced content extraction, semantic search, and RAG (Retrieval Augmented Generation) capabilities.

## Features

- **User Authentication**: JWT-based authentication with registration, login, and token refresh
- **Independent Chat Threads**: Create chat threads that work independently or optionally reference workspaces for context
- **Workspace Management**: Create and manage multiple workspaces focused on file management and RAG
- **Advanced File Processing**: Upload and process .txt, .csv, .docx files with content extraction and chunking
- **Dual Embedding System**: OpenAI embeddings with sentence-transformers fallback for robust text processing
- **Semantic Search**: Vector-based similarity search with text-based fallback
- **RAG Integration**: Enhanced responses using document context with similarity scoring
- **LangChain Integration**: Full OpenAI integration using LangChain for intelligent responses
- **Content Extraction**: Smart text chunking with overlap for optimal embedding performance
- **Duplicate Prevention**: Automatic duplicate file detection within workspaces
- **Processing Pipeline**: File status tracking (uploaded → processing → ready/failed)
- **Rate Limited**: Built-in rate limiting for API endpoints
- **Strong Validation**: Comprehensive input validation using Pydantic
- **MongoDB Integration**: Full MongoDB support for data persistence with vector search
- **File Storage**: Support for both local and S3-compatible storage

## Architecture Overview

### Independent Threads
- Threads are not bound to workspaces
- Each user owns their threads
- Threads can optionally reference a workspace for RAG context
- Full CRUD operations on threads

### Workspace-Centric File Management
- Workspaces focus on file storage and management
- Multiple users can be members of a workspace
- Files are processed with content extraction and embedding
- RAG functionality operates within workspace context
- Semantic search across all workspace documents

### Advanced Content Processing Pipeline
1. **File Upload** → Format validation (.txt, .csv, .docx)
2. **Content Extraction** → Smart text extraction with metadata
3. **Text Chunking** → 1000-char chunks with 100-char overlap
4. **Embedding Generation** → OpenAI or local sentence-transformers
5. **Vector Storage** → Embeddings stored with text chunks
6. **Semantic Search** → Cosine similarity matching for RAG

## Project Structure

```
backend/
├─ app.py                       # Flask app factory
├─ config/
│  ├─ __init__.py
│  ├─ settings.py               # Configuration with embedding settings
├─ extensions/
│  ├─ db.py                     # MongoDB client initialization
│  ├─ jwt.py                    # JWT configuration
│  ├─ limiter.py                # Rate limiting setup
│  ├─ storage.py                # File storage management (S3/local)
│  ├─ logger.py                 # Logging configuration
├─ models/                      # Pydantic models
│  ├─ user.py
│  ├─ workspace.py              # Workspace model (file-focused)
│  ├─ thread.py                 # Independent thread model
│  ├─ message.py
│  ├─ file.py                  # File models with processing status
│  ├─ embedding.py
├─ repositories/                # Data access layer
│  ├─ user_repo.py
│  ├─ workspace_repo.py         # File management focused
│  ├─ thread_repo.py            # Independent thread operations
│  ├─ message_repo.py
│  ├─ file_repo.py             # Enhanced with embedding search
├─ services/                    # Business logic
│  ├─ auth_service.py           # Authentication logic
│  ├─ chat_service.py           # Thread and messaging (with LangChain)
│  ├─ workspace_service.py      # Workspace and file management
│  ├─ file_service.py          # File upload, processing, search
│  ├─ embedding_service.py     # Dual embedding system
│  ├─ rag_service.py           # Enhanced RAG with semantic search
├─ blueprints/                  # REST API endpoints
│  ├─ auth_api.py               # Authentication endpoints
│  ├─ chat_api.py               # Thread and chat endpoints
│  ├─ file_api.py              # File management and search endpoints
├─ utils/
│  ├─ content_extractor.py     # Multi-format content extraction
│  ├─ exceptions.py             # Custom exceptions
│  ├─ validators.py             # Input validation utilities
│  ├─ pagination.py             # Pagination helpers
└─ requirements.txt            # Updated with file processing deps
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- OpenAI API Key (for LangChain integration and OpenAI embeddings)
- Redis (optional, for rate limiting)

### Installation

1. **Clone the repository and navigate to the project directory**

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory:
   ```env
   # Flask Configuration
   SECRET_KEY=your-secret-key-change-in-production
   DEBUG=True
   
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017/ai_chatbot
   MONGODB_DB_NAME=ai_chatbot
   
   # JWT Configuration
   JWT_SECRET_KEY=your-jwt-secret-key
   JWT_ACCESS_TOKEN_EXPIRES=3600
   JWT_REFRESH_TOKEN_EXPIRES=2592000
   
   # File Storage Configuration
   STORAGE_TYPE=local
   LOCAL_STORAGE_PATH=./uploads
   
   # OpenAI Configuration (Required for LangChain and embeddings)
   OPENAI_API_KEY=your-openai-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TEMPERATURE=0.7
   
   # Embedding Configuration
   EMBEDDING_MODEL=sentence-transformers  # or 'openai' for OpenAI embeddings
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002  # if using OpenAI embeddings
   LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2  # local model name
   
   # Redis Configuration (optional)
   REDIS_URL=redis://localhost:6379/0
   ```

5. **Start MongoDB:**
   Make sure MongoDB is running on your system.

6. **Run the application:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5000`

## API Endpoints

### Authentication

#### Register User
```http
POST /v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}
```

#### Login User
```http
POST /v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### Workspaces (File Management & RAG)

#### Create Workspace
```http
POST /v1/workspaces
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Documents Workspace"
}
```

#### Get User Workspaces
```http
GET /v1/workspaces?page=1&limit=20
Authorization: Bearer <access_token>
```

#### Get Threads Using Workspace
```http
GET /v1/workspaces/{workspace_id}/threads
Authorization: Bearer <access_token>
```

### File Management

#### Upload File (with Content Extraction & Embedding)
```http
POST /v1/workspaces/{workspace_id}/files
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
- file: [file.txt/.csv/.docx]
- title: "Optional file title" (optional)
```

#### Get Workspace Files
```http
GET /v1/workspaces/{workspace_id}/files?page=1&limit=20
Authorization: Bearer <access_token>
```

#### Get File Details
```http
GET /v1/files/{file_id}
Authorization: Bearer <access_token>
```

#### Delete File
```http
DELETE /v1/files/{file_id}
Authorization: Bearer <access_token>
```

#### Semantic Search Files
```http
POST /v1/workspaces/{workspace_id}/files/search
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "query": "project planning methodology",
  "top_k": 5
}
```

#### Get Supported File Formats
```http
GET /v1/workspaces/{workspace_id}/files/supported-formats
Authorization: Bearer <access_token>
```

### Independent Chat Threads

#### Create Thread (Independent)
```http
POST /v1/threads
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My Chat Thread",
  "workspace_id": "optional-workspace-id-for-rag"
}
```

#### Get User's Threads
```http
GET /v1/threads?page=1&limit=20
Authorization: Bearer <access_token>
```

#### Update Thread
```http
PATCH /v1/threads/{thread_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "workspace_id": "new-workspace-id-or-null"
}
```

#### Delete Thread
```http
DELETE /v1/threads/{thread_id}
Authorization: Bearer <access_token>
```

### Messages

#### Send Message (with Enhanced RAG)
```http
POST /v1/threads/{thread_id}/messages
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "What does the project documentation say about deployment strategies?",
  "use_rag": true,
  "top_k": 5,
  "temperature": 0.7
}
```

#### Get Thread Messages
```http
GET /v1/threads/{thread_id}/messages?page=1&limit=50
Authorization: Bearer <access_token>
```

## Testing the Enhanced File System

### 1. Upload and Process Documents
```bash
# Upload a text file
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@project_plan.txt" \
  -F "title=Project Planning Document"

# Upload a CSV file
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@data.csv"

# Upload a DOCX file
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@requirements.docx"
```

### 2. Check Processing Status
```bash
curl -X GET http://localhost:5000/v1/files/{file_id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Perform Semantic Search
```bash
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "deployment strategy and requirements",
    "top_k": 3
  }'
```

### 4. Create RAG-Enhanced Chat
```bash
# Create thread with workspace reference
curl -X POST http://localhost:5000/v1/threads \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Project Discussion",
    "workspace_id": "YOUR_WORKSPACE_ID"
  }'

# Send message with RAG
curl -X POST http://localhost:5000/v1/threads/{thread_id}/messages \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Based on our project documents, what are the key deployment considerations?",
    "use_rag": true,
    "top_k": 5
  }'
```

## File Processing Pipeline

### Supported Formats
- **`.txt`** - Plain text files (UTF-8, Latin-1 fallback)
- **`.csv`** - Comma-separated values (parsed with pandas)
- **`.docx`** - Microsoft Word documents (paragraph extraction)

### Processing Flow
1. **Upload Validation** → File format, size (50MB max), duplicates
2. **Content Extraction** → Format-specific text extraction
3. **Smart Chunking** → 1000 characters with 100-character overlap
4. **Embedding Generation** → OpenAI API or local sentence-transformers
5. **Storage** → Chunks with embeddings stored in MongoDB
6. **Status Updates** → uploaded → processing → ready/failed

### Embedding Options
- **OpenAI Embeddings** → `text-embedding-ada-002` (1536 dimensions)
- **Local Embeddings** → `all-MiniLM-L6-v2` (384 dimensions, offline)
- **Automatic Fallback** → Graceful degradation if services unavailable

## Key Architecture Changes

### Before (Basic File Support)
- Simple file upload without processing
- No content extraction or search
- Basic text matching for RAG

### After (Advanced File System)
- ✅ **Multi-format Processing** - .txt, .csv, .docx with smart extraction
- ✅ **Dual Embedding System** - OpenAI + local model fallback
- ✅ **Semantic Search** - Vector similarity with cosine distance
- ✅ **Smart Chunking** - Optimal chunk size with word boundary detection
- ✅ **Processing Pipeline** - Status tracking and error handling
- ✅ **Duplicate Prevention** - Filename-based duplicate detection
- ✅ **Enhanced RAG** - Document context with similarity scores
- ✅ **Comprehensive API** - Full CRUD operations for files

## Current Implementation Status

**✅ FULLY IMPLEMENTED:**
- Independent thread architecture with optional workspace references
- Advanced file upload with multi-format content extraction
- Dual embedding system (OpenAI + sentence-transformers)
- Semantic search using vector similarity
- Enhanced RAG with document context and scoring
- LangChain + OpenAI integration for intelligent responses
- Smart text chunking with overlap for optimal embeddings
- Processing pipeline with status tracking
- Comprehensive file management API
- Duplicate file prevention
- Strong input validation and error handling

**🚧 READY FOR EXTENSION:**
- Background job processing for large files
- Additional file formats (PDF, HTML, etc.)
- Vector database integration (Pinecone, Qdrant)
- Advanced chunking strategies
- Real-time file processing notifications
- Workspace collaboration features
- File versioning and history

## Benefits of Enhanced Architecture

1. **Intelligent Search** - Semantic understanding vs keyword matching
2. **Multi-format Support** - Process diverse document types
3. **Robust Embeddings** - Dual system ensures availability
4. **Smart Processing** - Optimal chunking for better context
5. **RAG Enhancement** - High-quality document grounding
6. **User Experience** - Status tracking and error handling
7. **Scalability** - Modular design for easy extension

## Performance Considerations

### Embedding Models
- **OpenAI**: Higher quality, API cost, internet required
- **Local**: Free, offline, smaller model size, faster for small batches
- **Automatic Selection**: Falls back gracefully based on availability

### Chunking Strategy
- **Chunk Size**: 1000 characters (optimal for embeddings)
- **Overlap**: 100 characters (maintains context continuity)
- **Word Boundaries**: Smart splitting to preserve meaning

### Search Performance
- **Vector Search**: O(n) similarity calculation
- **Text Fallback**: MongoDB text search for reliability
- **Caching**: Results cached for repeated queries

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment variables
2. Use a production WSGI server like Gunicorn
3. Set up proper MongoDB and Redis instances
4. Configure OpenAI API key securely
5. Set up SSL/TLS certificates
6. Consider vector database for large-scale deployments

Example Gunicorn command:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:create_production_app
```

## Next Steps

To extend this implementation:

1. **Add Background Processing** - Celery/RQ for large file processing
2. **Implement Vector Database** - Pinecone, Qdrant, or Weaviate integration
3. **Add More File Formats** - PDF, HTML, PowerPoint support
4. **Advanced Chunking** - Semantic chunking, document structure awareness
5. **Real-time Updates** - WebSocket notifications for processing status
6. **Analytics Dashboard** - Usage metrics and search analytics
7. **Collaboration Features** - File sharing, comments, annotations
8. **Version Control** - File versioning and change tracking

## Environment Variables Reference

```env
# Core Application
SECRET_KEY=your-secret-key
DEBUG=False
MONGODB_URI=mongodb://localhost:27017/ai_chatbot

# Authentication  
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600

# OpenAI Integration
OPENAI_API_KEY=your-openai-key
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers  # or 'openai'
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# File Storage
STORAGE_TYPE=local  # or 's3'
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE=52428800  # 50MB

# Rate Limiting
REDIS_URL=redis://localhost:6379/0
RATELIMIT_DEFAULT=100 per hour
```

The implementation is now **production-ready** with advanced file processing, semantic search, and robust RAG capabilities! 