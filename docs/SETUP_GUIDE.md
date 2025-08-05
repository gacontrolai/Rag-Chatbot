# Setup and Installation Guide

Complete setup instructions for the RAG Chatbot project.

## System Requirements

### Prerequisites
- **Python 3.8+** (recommended: Python 3.10+)
- **Node.js 16+** (recommended: Node.js 18+)
- **MongoDB 4.4+** (local installation or MongoDB Atlas)
- **Redis** (optional, for rate limiting)
- **Git** for version control

### Hardware Requirements
- **Minimum**: 4GB RAM, 2GB free disk space
- **Recommended**: 8GB RAM, 5GB free disk space
- **For local embeddings**: Additional 2GB RAM

## Quick Start (5 minutes)

### 1. Clone and Navigate
```bash
git clone https://github.com/gacontrolai/Rag-Chatbot.git
cd Rag-Chatbot
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
```

### 4. Environment Configuration

**Backend** - Create `backend/.env`:
```env
# Basic Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
MONGODB_URI=mongodb://localhost:27017/ai_chatbot
MONGODB_DB_NAME=ai_chatbot

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# OpenAI Configuration (Required)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# File Storage
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE=52428800
```

**Frontend** - Create `frontend/.env`:
```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

### 5. Start the Application
```bash
# Terminal 1 - Backend
cd backend
python app.py

# Terminal 2 - Frontend  
cd frontend
npm start
```

### 6. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Detailed Installation

### Backend Setup (Python/Flask)

#### 1. Python Environment
```bash
# Check Python version
python --version

# Create virtual environment
cd backend
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Windows Command Prompt:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Verify activation
which python  # Should point to venv
```

#### 2. Install Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list

# Install additional development tools (optional)
pip install pytest black flake8
```

#### 3. Database Setup

**Option A: Local MongoDB**
1. Download and install MongoDB Community Edition
2. Start MongoDB service:
   ```bash
   # Windows (as service)
   net start MongoDB
   
   # Linux
   sudo systemctl start mongod
   
   # Mac
   brew services start mongodb-community
   ```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://www.mongodb.com/atlas
2. Create free cluster
3. Get connection string
4. Update `MONGODB_URI` in `.env`

#### 4. Redis Setup (Optional)
```bash
# Windows (using Chocolatey)
choco install redis-64

# Linux
sudo apt-get install redis-server

# Mac
brew install redis

# Start Redis
redis-server
```

### Frontend Setup (React/Node.js)

#### 1. Node.js Installation
```bash
# Check Node.js version
node --version
npm --version

# If not installed, download from https://nodejs.org/
```

#### 2. Project Dependencies
```bash
cd frontend

# Install dependencies
npm install

# Install additional development tools (optional)
npm install -D eslint prettier

# Verify installation
npm list
```

#### 3. Development Server
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test
```

## Configuration Details

### Environment Variables

#### Backend Configuration (`backend/.env`)
```env
# ============ CORE APPLICATION ============
SECRET_KEY=your-secret-key-change-in-production
DEBUG=True
FLASK_ENV=development

# ============ DATABASE ============
MONGODB_URI=mongodb://localhost:27017/ai_chatbot
MONGODB_DB_NAME=ai_chatbot

# ============ AUTHENTICATION ============
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# ============ OPENAI INTEGRATION ============
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# ============ EMBEDDING CONFIGURATION ============
EMBEDDING_MODEL=sentence-transformers  # or 'openai'
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
LOCAL_EMBEDDING_MODEL=all-MiniLM-L6-v2

# ============ FILE STORAGE ============
STORAGE_TYPE=local  # or 's3'
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE=52428800  # 50MB in bytes

# S3 Configuration (if using S3)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1

# ============ RATE LIMITING ============
REDIS_URL=redis://localhost:6379/0
RATELIMIT_DEFAULT=100 per hour
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# ============ LOGGING ============
LOG_LEVEL=INFO
LOG_FILE=app.log

# ============ CORS ============
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

#### Frontend Configuration (`frontend/.env`)
```env
# API Configuration
REACT_APP_API_BASE_URL=http://localhost:5000

# Optional: Custom configuration
REACT_APP_MAX_FILE_SIZE=50
REACT_APP_SUPPORTED_FORMATS=txt,csv,docx
REACT_APP_APP_NAME=RAG Chatbot

# Development
GENERATE_SOURCEMAP=false
SKIP_PREFLIGHT_CHECK=true
```

### File Structure After Setup
```
Rag-Chatbot/
├── backend/
│   ├── venv/                 # Virtual environment
│   ├── uploads/              # File storage (created automatically)
│   ├── .env                  # Environment variables
│   └── ... (source files)
├── frontend/
│   ├── node_modules/         # NPM packages
│   ├── build/                # Production build (after npm run build)
│   ├── .env                  # Environment variables
│   └── ... (source files)
└── docs/
    └── ... (documentation)
```

## Verification and Testing

### 1. Backend Health Check
```bash
# With backend running, test health endpoint
curl http://localhost:5000/health

# Should return:
# {"status": "healthy", "timestamp": "..."}
```

### 2. Frontend Verification
- Open http://localhost:3000
- You should see the login page
- Register a new account
- Try creating a workspace

### 3. Full Integration Test
```bash
# Register user
curl -X POST http://localhost:5000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123","name":"Test User"}'

# Login and get token
curl -X POST http://localhost:5000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123"}'
```

## Troubleshooting

### Common Issues

#### Python/Backend Issues
```bash
# Issue: Module not found
# Solution: Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Issue: MongoDB connection error
# Solution: Check MongoDB is running
# Windows: net start MongoDB
# Linux: sudo systemctl status mongod

# Issue: OpenAI API errors
# Solution: Verify API key in .env file
echo $OPENAI_API_KEY  # Should not be empty
```

#### Node.js/Frontend Issues
```bash
# Issue: npm install fails
# Solution: Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Issue: Port 3000 already in use
# Solution: Use different port
PORT=3001 npm start

# Issue: CORS errors
# Solution: Check REACT_APP_API_BASE_URL in .env
```

#### Database Issues
```bash
# MongoDB connection issues
# Check if MongoDB is running
mongo --eval "db.adminCommand('ismaster')"

# Reset database (if needed)
mongo ai_chatbot --eval "db.dropDatabase()"
```

### Performance Optimization

#### Backend Optimization
```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Monitor performance
pip install flask-monitoring-dashboard
```

#### Frontend Optimization
```bash
# Analyze bundle size
npm install -g webpack-bundle-analyzer
npm run build
npx webpack-bundle-analyzer build/static/js/*.js

# Enable compression
npm install -g serve
serve -s build -l 3000
```

## Development Workflow

### 1. Development Mode
```bash
# Backend with auto-reload
cd backend
export FLASK_ENV=development
python app.py

# Frontend with hot reload
cd frontend
npm start
```

### 2. Production Mode
```bash
# Backend production server
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:create_production_app

# Frontend production build
cd frontend
npm run build
npx serve -s build
```

### 3. Docker Setup (Optional)
```bash
# Build and run with Docker
docker-compose up --build

# Or run separately
docker build -t rag-backend ./backend
docker build -t rag-frontend ./frontend
```

## Next Steps

After successful setup:

1. **Explore the Application**
   - Register an account
   - Create a workspace  
   - Upload a document
   - Start a chat conversation

2. **Customize Configuration**
   - Adjust embedding models
   - Configure file storage
   - Set up production database

3. **Deploy to Production**
   - Set up cloud hosting
   - Configure domain and SSL
   - Set up monitoring

4. **Extend Functionality**
   - Add new file formats
   - Implement additional features
   - Integrate with other services

## Support

If you encounter issues:

1. **Check the logs** for error messages
2. **Verify environment variables** are set correctly
3. **Ensure all services** (MongoDB, Redis) are running
4. **Check the troubleshooting section** above
5. **Open an issue** on GitHub with detailed information

Happy coding! 🚀
