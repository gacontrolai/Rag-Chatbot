# RAG Chatbot - Intelligent Document Q&A System

A comprehensive full-stack chatbot application that combines **Retrieval Augmented Generation (RAG)** with advanced file processing capabilities. Upload documents, create workspaces, and have intelligent conversations about your content using OpenAI's GPT models and **Pinecone vector database**.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![React](https://img.shields.io/badge/react-18.2.0-blue)
![Pinecone](https://img.shields.io/badge/pinecone-vector--db-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 🚀 Features

### 🤖 **Intelligent RAG System**
- **Pinecone Vector Database**: High-performance vector search with 1536-dimensional embeddings
- **Semantic Search**: Vector-based similarity search with dual embedding models (OpenAI + Sentence Transformers)
- **Multi-format Processing**: Support for `.txt`, `.csv`, `.docx` files with smart content extraction
- **Advanced Chunking**: Optimal text segmentation with 1000-char chunks and 100-char overlap
- **Context-Aware Q&A**: LangChain integration for enhanced responses using document context

### 🏢 **Workspace Management**
- **Independent Threads**: Chat threads that work standalone or reference workspaces
- **Multi-user Workspaces**: Collaborative document management
- **File Organization**: Structured file storage with processing pipeline
- **Duplicate Prevention**: Automatic duplicate detection and handling

### 🔐 **Authentication & Security**
- **JWT Authentication**: Secure login/register with token refresh
- **Rate Limiting**: Built-in API protection
- **Input Validation**: Comprehensive validation using Pydantic
- **Secure Storage**: Support for local and S3-compatible storage

### 🎨 **Modern Frontend**
- **React 18**: Modern React application with hooks and context
- **Responsive Design**: Mobile-first design that works on all devices
- **Real-time Chat**: Interactive chat interface with message history
- **File Management**: Drag-and-drop upload with progress tracking

## 📋 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+**
- **MongoDB** (local or Atlas)
- **OpenAI API Key**
- **Pinecone API Key** (for vector database)
- **Redis** (optional, for rate limiting)

### 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/gacontrolai/Rag-Chatbot.git
   cd Rag-Chatbot
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   
   **Backend** - Create `backend/.env`:
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
   
   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key-here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TEMPERATURE=0.7
   
   # Embedding Configuration
   EMBEDDING_MODEL=sentence-transformers  # or 'openai'
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
   LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2
   
   # Pinecone Configuration (Primary Vector Database)
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_ENVIRONMENT=us-east1-gcp
   PINECONE_INDEX_NAME=rag-chatbot
   VECTOR_STORE=pinecone  # 'pinecone' or 'mongodb'
   
   # File Storage
   STORAGE_TYPE=local
   LOCAL_STORAGE_PATH=./uploads
   MAX_FILE_SIZE=52428800  # 50MB
   
   # Redis (optional)
   REDIS_URL=redis://localhost:6379/0
   ```

   **Frontend** - Create `frontend/.env`:
   ```env
   REACT_APP_API_BASE_URL=http://localhost:5000
   ```

5. **Start the Application**
   
   **Backend** (Terminal 1):
   ```bash
   cd backend
   python app.py
   ```
   
   **Frontend** (Terminal 2):
   ```bash
   cd frontend
   npm start
   ```

6. **Access the Application**
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:5000`

## 🏗️ Architecture

```
Rag-Chatbot/
├── backend/                 # Flask API Server
│   ├── app.py              # Application factory
│   ├── blueprints/         # API route handlers
│   ├── services/           # Business logic layer
│   │   ├── pinecone_service.py    # Pinecone vector operations
│   │   ├── vector_service.py      # Unified vector store interface
│   │   ├── embedding_service.py   # Dual embedding system
│   │   └── file_service.py        # File processing pipeline
│   ├── repositories/       # Data access layer
│   ├── models/             # Pydantic data models
│   ├── utils/              # Utility functions
│   └── requirements.txt    # Python dependencies (includes pinecone-client)
├── frontend/               # React Client Application
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API integration
│   │   ├── context/        # React context providers
│   │   └── utils/          # Helper functions
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
└── README.md              # This file
```

### 🔄 **Processing Pipeline**

1. **File Upload** → Format validation & duplicate check
2. **Content Extraction** → Smart text extraction by file type
3. **Text Chunking** → Optimal segmentation with overlap
4. **Embedding Generation** → Vector representation (OpenAI/Local)
5. **Pinecone Storage** → High-performance vector indexing with metadata
6. **RAG Processing** → Context-aware response generation with similarity search

## 📚 API Documentation

### Authentication
```bash
# Register user
POST /v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "name": "John Doe"
}

# Login
POST /v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

### File Management
```bash
# Upload file
POST /v1/workspaces/{workspace_id}/files
Content-Type: multipart/form-data

# Semantic search (powered by Pinecone)
POST /v1/workspaces/{workspace_id}/files/search
{
  "query": "project requirements",
  "top_k": 5
}

# Get vector store statistics
GET /v1/vector-store/stats
```

### Chat & Messaging
```bash
# Create thread
POST /v1/threads
{
  "title": "Discussion Thread",
  "workspace_id": "optional-workspace-id"
}

# Send message with RAG
POST /v1/threads/{thread_id}/messages
{
  "content": "What are the deployment requirements?",
  "use_rag": true,
  "top_k": 5
}
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
```bash
cd frontend
npm test
```

### Integration Testing
```bash
# Test file upload and processing
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_document.txt"

# Test Pinecone-powered semantic search
curl -X POST http://localhost:5000/v1/workspaces/{workspace_id}/files/search \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "top_k": 3}'

# Check vector store statistics
curl -X GET http://localhost:5000/v1/vector-store/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🚀 Deployment

### Production Configuration

1. **Environment Variables**
   ```env
   DEBUG=False
   SECRET_KEY=production-secret-key
   MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/
   OPENAI_API_KEY=production-openai-key
   PINECONE_API_KEY=production-pinecone-key
   PINECONE_ENVIRONMENT=production-environment
   ```

2. **Backend Deployment**
   ```bash
   # Using Gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:create_production_app
   ```

3. **Frontend Deployment**
   ```bash
   # Build for production
   npm run build
   
   # Serve static files
   npx serve -s build -l 3000
   ```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## 🔧 Configuration Options

### Vector Database Options
- **Pinecone (Primary)**: High-performance managed vector database
  - **Dimensions**: 1536 (OpenAI embeddings) or 384 (local embeddings)
  - **Metric**: Cosine similarity
  - **Automatic scaling** and **high availability**
  - **Metadata filtering** for workspace isolation
- **MongoDB (Fallback)**: Local vector storage when Pinecone unavailable
  - **Automatic fallback** if Pinecone initialization fails
  - **Graceful degradation** for development environments

### Embedding Models
- **OpenAI Embeddings**: High quality, requires API key, 1536 dimensions
- **Local Embeddings**: Free, offline, 384 dimensions (all-MiniLM-L6-v2)
- **Automatic Fallback**: Graceful degradation if services unavailable

### File Processing
- **Supported Formats**: `.txt`, `.csv`, `.docx`
- **Maximum File Size**: 50MB (configurable)
- **Chunk Size**: 1000 characters with 100-character overlap
- **Processing Status**: `uploaded` → `processing` → `ready`/`failed`

### Storage Options
- **Local Storage**: Files stored in local filesystem
- **S3-Compatible**: AWS S3, MinIO, or other S3-compatible storage
- **Database**: MongoDB for metadata and file records
- **Vector Storage**: Pinecone for embeddings and similarity search

## 🌟 Pinecone Integration Benefits

### Performance Advantages
- **Sub-second Search**: Optimized vector similarity search
- **Horizontal Scaling**: Handles millions of vectors efficiently
- **Real-time Updates**: Immediate availability of new embeddings
- **High Availability**: Managed infrastructure with 99.9% uptime

### Advanced Features
- **Metadata Filtering**: Workspace-level data isolation
- **Batch Operations**: Efficient bulk upserts and deletions
- **Multiple Indexes**: Support for different embedding dimensions
- **Analytics**: Built-in query performance metrics

### Cost Optimization
- **Pay-per-use**: Only pay for active vector storage and queries
- **Automatic Scaling**: No need to provision capacity upfront
- **Efficient Storage**: Compressed vector representations

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint/Prettier for JavaScript code
- Write tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues
- **CORS Errors**: Ensure backend allows frontend origin
- **File Upload Fails**: Check file format and size limits
- **Pinecone Connection**: Verify API key and environment settings
- **Embedding Errors**: Verify OpenAI API key or fallback to local model
- **MongoDB Connection**: Ensure MongoDB is running and accessible

### Getting Help
- 📧 **Email**: [your-email@example.com](mailto:your-email@example.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/gacontrolai/Rag-Chatbot/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/gacontrolai/Rag-Chatbot/wiki)

## 🙏 Acknowledgments

- **Pinecone** for high-performance vector database
- **OpenAI** for GPT models and embeddings
- **LangChain** for RAG framework
- **Sentence Transformers** for local embeddings
- **React** for frontend framework
- **Flask** for backend API
- **MongoDB** for data storage

---

**Built with ❤️ by the RAG Chatbot Team**

⭐ **Star this repository if you found it helpful!**
