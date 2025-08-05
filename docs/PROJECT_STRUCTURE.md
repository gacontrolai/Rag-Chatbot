# Project Structure

This document outlines the complete project structure for the RAG Chatbot application.

## Root Directory
```
Rag-Chatbot/
├── README.md                 # Main project documentation
├── .gitignore               # Git ignore rules for entire project
├── LICENSE                  # Project license (if applicable)
├── backend/                 # Python Flask API server
├── frontend/                # React client application
└── docs/                    # Project documentation
```

## Backend Structure (`/backend`)
```
backend/
├── app.py                   # Flask application factory
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Environment variables (gitignored)
├── uploads/                # Local file storage (gitignored)
├── blueprints/             # API route handlers
│   ├── __init__.py
│   ├── auth_api.py         # Authentication endpoints
│   ├── chat_api.py         # Chat and thread endpoints
│   └── file_api.py         # File management endpoints
├── config/                 # Configuration modules
│   ├── __init__.py
│   └── settings.py         # Application settings
├── extensions/             # Flask extensions
│   ├── __init__.py
│   ├── db.py              # MongoDB connection
│   ├── jwt.py             # JWT configuration
│   ├── limiter.py         # Rate limiting setup
│   ├── logger.py          # Logging configuration
│   └── storage.py         # File storage management
├── models/                 # Pydantic data models
│   ├── __init__.py
│   ├── user.py            # User model
│   ├── workspace.py       # Workspace model
│   ├── thread.py          # Chat thread model
│   ├── message.py         # Message model
│   ├── file.py            # File model
│   └── embedding.py       # Embedding model
├── repositories/           # Data access layer
│   ├── __init__.py
│   ├── user_repo.py       # User data operations
│   ├── workspace_repo.py  # Workspace data operations
│   ├── thread_repo.py     # Thread data operations
│   ├── message_repo.py    # Message data operations
│   └── file_repo.py       # File data operations
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── auth_service.py    # Authentication logic
│   ├── chat_service.py    # Chat and messaging logic
│   ├── workspace_service.py # Workspace management
│   ├── file_service.py    # File processing and management
│   ├── embedding_service.py # Embedding generation
│   └── rag_service.py     # RAG implementation
└── utils/                  # Utility functions
    ├── __init__.py
    ├── content_extractor.py # File content extraction
    ├── text_extractor.py   # Text processing utilities
    ├── exceptions.py       # Custom exceptions
    ├── pagination.py       # Pagination helpers
    └── validators.py       # Input validation
```

## Frontend Structure (`/frontend`)
```
frontend/
├── package.json            # Node.js dependencies and scripts
├── package-lock.json       # Dependency lock file
├── .env.example           # Environment variables template
├── .env                   # Environment variables (gitignored)
├── public/                # Static assets
│   ├── index.html         # HTML template
│   └── manifest.json      # PWA manifest
├── build/                 # Production build (gitignored)
├── node_modules/          # NPM packages (gitignored)
└── src/                   # React source code
    ├── index.js           # Application entry point
    ├── App.js             # Main App component
    ├── components/        # Reusable UI components
    │   ├── ChatInterface.js # Chat interface component
    │   ├── FileManager.js   # File upload and management
    │   ├── Header.js        # Application header
    │   ├── ProtectedRoute.js # Route protection
    │   └── Tabs.js          # Tab navigation component
    ├── context/           # React context providers
    │   ├── AuthContext.js   # Authentication state
    │   └── WorkspaceContext.js # Workspace state
    ├── pages/             # Page components
    │   ├── Dashboard.js     # Main dashboard page
    │   ├── Login.js         # Login page
    │   ├── Register.js      # Registration page
    │   ├── PublicChat.js    # Public chat page
    │   └── Workspace.js     # Workspace management page
    ├── services/          # API integration
    │   ├── api.js           # Axios configuration
    │   └── apiService.js    # API service functions
    ├── styles/            # CSS stylesheets
    │   └── App.css          # Main application styles
    └── utils/             # Utility functions
        └── helpers.js       # Helper functions
```

## Documentation Structure (`/docs`)
```
docs/
├── API_DOCUMENTATION.md    # Complete API reference
├── SETUP_GUIDE.md         # Detailed setup instructions
├── DEPLOYMENT.md          # Deployment guidelines (if created)
├── CONTRIBUTING.md        # Contribution guidelines (if created)
└── ARCHITECTURE.md        # Technical architecture overview (if created)
```

## Key Configuration Files

### Environment Files
- `backend/.env` - Backend environment variables
- `frontend/.env` - Frontend environment variables
- `backend/.env.example` - Backend environment template
- `frontend/.env.example` - Frontend environment template

### Package Management
- `backend/requirements.txt` - Python dependencies
- `frontend/package.json` - Node.js dependencies and scripts

### Git Configuration
- `.gitignore` - Comprehensive ignore rules for both backend and frontend

## Data Flow Architecture

```
Frontend (React) 
    ↓ HTTP/HTTPS
Backend API (Flask)
    ↓ 
Business Logic (Services)
    ↓
Data Access (Repositories)
    ↓
Database (MongoDB)
```

## File Processing Pipeline

```
File Upload → Content Extraction → Text Chunking → Embedding Generation → Vector Storage → RAG Query
```

## Key Patterns

### Backend Patterns
- **Repository Pattern**: Separate data access from business logic
- **Service Layer**: Encapsulate business rules and operations
- **Blueprint Organization**: Group related API endpoints
- **Factory Pattern**: Application factory for configuration
- **Dependency Injection**: Clean separation of concerns

### Frontend Patterns
- **Component Composition**: Reusable UI components
- **Context API**: Global state management
- **Service Layer**: API communication abstraction
- **Protected Routes**: Authentication-based navigation
- **Responsive Design**: Mobile-first approach

## Development Workflow

1. **Backend Development**: Start with models → repositories → services → APIs
2. **Frontend Development**: Create pages → components → services → integration
3. **Testing**: Unit tests → integration tests → end-to-end tests
4. **Deployment**: Development → staging → production

## Security Considerations

- Environment variables for sensitive data
- JWT token-based authentication
- Input validation and sanitization
- Rate limiting on API endpoints
- CORS configuration
- File upload security checks

This structure promotes:
- **Separation of Concerns**: Clear boundaries between layers
- **Scalability**: Easy to add new features and components
- **Maintainability**: Well-organized code structure
- **Testability**: Each layer can be tested independently
- **Security**: Proper handling of sensitive data and authentication
