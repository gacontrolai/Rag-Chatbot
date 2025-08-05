# RAG Chatbot Backend

Flask-based backend API for the RAG Chatbot system with advanced file processing, semantic search, and RAG capabilities.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

## Key Features

- **RAG Integration**: LangChain + OpenAI for intelligent document Q&A
- **Dual Embedding System**: OpenAI embeddings with sentence-transformers fallback
- **Multi-format Processing**: Support for .txt, .csv, .docx files
- **Semantic Search**: Vector-based similarity search with MongoDB
- **JWT Authentication**: Secure user authentication with token refresh
- **Independent Threads**: Chat threads with optional workspace context
- **Rate Limiting**: Built-in API protection
- **File Storage**: Local and S3-compatible storage options

## Environment Configuration

Required environment variables in `.env`:

```env
# Core
SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017/ai_chatbot
JWT_SECRET_KEY=your-jwt-secret

# OpenAI (Required)
OPENAI_API_KEY=your-openai-api-key

# Embedding Model
EMBEDDING_MODEL=sentence-transformers  # or 'openai'

# Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads
```

## API Endpoints

### Authentication
- `POST /v1/auth/register` - Register user
- `POST /v1/auth/login` - Login user
- `POST /v1/auth/refresh` - Refresh token

### Workspaces & Files
- `POST /v1/workspaces` - Create workspace
- `POST /v1/workspaces/{id}/files` - Upload file
- `POST /v1/workspaces/{id}/files/search` - Semantic search

### Chat & Threads
- `POST /v1/threads` - Create thread
- `POST /v1/threads/{id}/messages` - Send message with RAG

## Architecture

```
app.py (Flask Factory)
├── blueprints/     # API endpoints
├── services/       # Business logic
├── repositories/   # Data access
├── models/         # Pydantic models
├── utils/          # Utilities
└── extensions/     # Flask extensions
```

## File Processing Pipeline

1. **Upload** → Format validation
2. **Extract** → Smart content extraction
3. **Chunk** → 1000-char chunks with overlap
4. **Embed** → Vector generation (OpenAI/local)
5. **Store** → MongoDB with vector search
6. **RAG** → Context-aware responses

## Dependencies

### Core Framework
- Flask 2.3.3 - Web framework
- flask-smorest - API framework
- flask-jwt-extended - JWT authentication

### AI & ML
- openai - GPT models
- langchain - RAG framework
- sentence-transformers - Local embeddings

### Database & Storage
- pymongo - MongoDB driver
- boto3 - S3 storage

### File Processing
- python-docx - Word documents
- pandas - CSV processing

## Development

```bash
# Install dev dependencies
pip install pytest black flake8

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

## Production Deployment

```bash
# Install Gunicorn
pip install gunicorn

# Run production server
gunicorn -w 4 -b 0.0.0.0:5000 app:create_production_app
```

## Documentation

For complete documentation, see the main project documentation at the repository root.
