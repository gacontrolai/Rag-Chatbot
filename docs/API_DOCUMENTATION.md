# API Documentation

Complete API reference for the RAG Chatbot backend.

## Base URL
```
http://localhost:5000  (Development)
https://api.yourdomain.com  (Production)
```

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication APIs (/v1/auth)

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

**Response:**
```json
{
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "name": "John Doe",
    "plan": "free",
    "created_at": "2025-08-06T10:00:00Z",
    "updated_at": "2025-08-06T10:00:00Z"
  },
  "tokens": {
    "access_token": "jwt_access_token",
    "refresh_token": "jwt_refresh_token"
  }
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

#### Refresh Token
```http
POST /v1/auth/refresh
Authorization: Bearer <refresh_token>
```

**Note**: The refresh token must be sent in the Authorization header, not in the request body.

#### Get Current User
```http
GET /v1/auth/me
Authorization: Bearer <access_token>
```

### Workspace APIs (/v1)

#### Create Workspace
```http
POST /v1/workspaces
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Documents Workspace",
  "description": "Workspace for project documents"
}
```

#### Get User Workspaces
```http
GET /v1/workspaces?page=1&limit=20
Authorization: Bearer <access_token>
```

#### Get Workspace Details
```http
GET /v1/workspaces/{workspace_id}
Authorization: Bearer <access_token>
```

#### Get Workspace Threads
```http
GET /v1/workspaces/{workspace_id}/threads
Authorization: Bearer <access_token>
```

### Thread APIs (/v1)

#### Create Thread
```http
POST /v1/threads
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My Chat Thread",
  "workspace_id": "optional-workspace-id-for-rag"
}
```

#### Get User Threads
```http
GET /v1/threads?page=1&limit=20
Authorization: Bearer <access_token>
```

#### Get Thread Details
```http
GET /v1/threads/{thread_id}
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

### Message APIs (/v1)

#### Send Message
```http
POST /v1/threads/{thread_id}/messages
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "What does the project documentation say about deployment?",
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

### File Management APIs (/v1)

#### Upload File
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

## Error Responses

All errors follow this format:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR` - Input validation failed
- `AUTHENTICATION_REQUIRED` - Missing or invalid token
- `PERMISSION_DENIED` - User lacks required permissions
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `FILE_PROCESSING_ERROR` - Error during file processing
- `RATE_LIMIT_EXCEEDED` - Too many requests

## Rate Limiting

API endpoints are rate limited:
- **Authentication**: 5 requests per minute
- **File Upload**: 10 files per hour
- **General APIs**: 100 requests per hour

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```
