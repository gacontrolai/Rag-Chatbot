# 📋 **RAG Chatbot Integration Test Plan**

## 🎯 **Overview**
Comprehensive API testing plan for the RAG Chatbot backend with 3 happy path cases and 3 failure cases for each endpoint.

**Test Environment:**
- Backend: `http://localhost:5000`
- Frontend: `http://localhost:3000`
- Database: MongoDB Atlas
- Vector Store: Pinecone
- AI Provider: OpenAI

---

## 🔐 **Authentication APIs**

### **1. POST /v1/auth/register**

**Happy Path Cases:**

1. **Valid New User Registration**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "John Doe", "email": "john@example.com", "password": "SecurePass123!"}'
   ```
   - Expected: 201 Created, user object + tokens returned

2. **Registration with Minimum Valid Data**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "A", "email": "a@b.co", "password": "Pass123!"}'
   ```
   - Expected: 201 Created, valid user created with minimal data

3. **Registration with Maximum Length Fields**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "Very Long Name That Is Exactly One Hundred Characters Long For Testing Maximum Length Validation", "email": "very.long.email.address.for.testing.purposes@verylongdomainname.com", "password": "VeryLongPasswordThatMeetsAllRequirements123!"}'
   ```
   - Expected: 201 Created, handles maximum length fields

**Failure Cases:**

1. **Duplicate Email Registration**
   ```powershell
   # First registration
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "User1", "email": "duplicate@test.com", "password": "Pass123!"}'
   # Duplicate registration
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "User2", "email": "duplicate@test.com", "password": "Pass456!"}'
   ```
   - Expected: 400/409 Conflict, "Email already exists" error

2. **Invalid Email Format**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "Test User", "email": "invalid-email", "password": "Pass123!"}'
   ```
   - Expected: 400 Bad Request, validation error for invalid email

3. **Missing Required Fields**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"email": "test@example.com"}'
   ```
   - Expected: 400 Bad Request, "Missing required fields" error

---

### **2. POST /v1/auth/login**

**Happy Path Cases:**

1. **Valid Login with Existing User**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "SecurePass123!"}'
   ```
   - Expected: 200 OK, user object + tokens returned

2. **Case Insensitive Email Login**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "JOHN@EXAMPLE.COM", "password": "SecurePass123!"}'
   ```
   - Expected: 200 OK, login succeeds with uppercase email

3. **Login After Previous Session**
   ```powershell
   # Login multiple times with same credentials
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "SecurePass123!"}'
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "SecurePass123!"}'
   ```
   - Expected: 200 OK both times, new tokens generated

**Failure Cases:**

1. **Invalid Password**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "WrongPassword123!"}'
   ```
   - Expected: 401 Unauthorized, "Invalid credentials" error

2. **Non-existent Email**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "nonexistent@example.com", "password": "AnyPassword123!"}'
   ```
   - Expected: 401 Unauthorized, "Invalid credentials" error

3. **Empty/Missing Credentials**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{}'
   ```
   - Expected: 400 Bad Request, "Missing email/password" error

---

### **3. GET /v1/auth/me**

**Happy Path Cases:**

1. **Valid Token - Get Current User**
   ```powershell
   $token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # From login response
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, current user details returned

2. **Fresh Token After Login**
   ```powershell
   $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "SecurePass123!"}'
   $token = $loginResponse.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, user details match login user

3. **Token with Different User**
   ```powershell
   # Login as different user and get their details
   $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "test2@example.com", "password": "testpassword123"}'
   $token = $loginResponse.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, returns test2@example.com user details

**Failure Cases:**

1. **No Authorization Header**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET
   ```
   - Expected: 401 Unauthorized, "Missing authorization header" error

2. **Invalid Token**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET -Headers @{Authorization="Bearer invalid_token_here"}
   ```
   - Expected: 422 Unprocessable Entity, "Invalid token" error

3. **Expired Token**
   ```powershell
   $expiredToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MzQ1NjcwMDB9.expired"
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/me" -Method GET -Headers @{Authorization="Bearer $expiredToken"}
   ```
   - Expected: 422 Unprocessable Entity, "Token has expired" error

---

### **4. POST /v1/auth/refresh**

**Happy Path Cases:**

1. **Valid Refresh Token**
   ```powershell
   $loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/login" -Method POST -ContentType "application/json" -Body '{"email": "john@example.com", "password": "SecurePass123!"}'
   $refreshToken = $loginResponse.tokens.refresh_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $refreshToken"}
   ```
   - Expected: 200 OK, new access token returned

2. **Multiple Refresh Operations**
   ```powershell
   # Use refresh token multiple times
   $refreshResponse1 = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $refreshToken"}
   $refreshResponse2 = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $refreshToken"}
   ```
   - Expected: 200 OK, new tokens each time

3. **Refresh After Token Near Expiry**
   ```powershell
   # Wait until access token is close to expiry, then refresh
   Start-Sleep -Seconds 3590  # Wait near token expiry
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $refreshToken"}
   ```
   - Expected: 200 OK, successful refresh near expiry

**Failure Cases:**

1. **Access Token Instead of Refresh Token**
   ```powershell
   $accessToken = $loginResponse.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $accessToken"}
   ```
   - Expected: 422 Unprocessable Entity, "Invalid token type" error

2. **Expired Refresh Token**
   ```powershell
   $expiredRefreshToken = "expired_refresh_token_here"
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer $expiredRefreshToken"}
   ```
   - Expected: 422 Unprocessable Entity, "Refresh token expired" error

3. **Invalid Refresh Token Format**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/refresh" -Method POST -Headers @{Authorization="Bearer invalid_format"}
   ```
   - Expected: 422 Unprocessable Entity, "Invalid token format" error

---

## 🏢 **Workspace APIs**

### **5. POST /v1/workspaces**

**Happy Path Cases:**

1. **Create Basic Workspace**
   ```powershell
   $token = $loginResponse.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "My First Workspace", "description": "Test workspace"}'
   ```
   - Expected: 201 Created, workspace object with ID returned

2. **Create Workspace with Minimal Data**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "MinWorkspace"}'
   ```
   - Expected: 201 Created, workspace with name only

3. **Create Multiple Workspaces for Same User**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Workspace 1", "description": "First workspace"}'
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Workspace 2", "description": "Second workspace"}'
   ```
   - Expected: 201 Created for both, different workspace IDs

**Failure Cases:**

1. **Unauthorized Request (No Token)**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Body '{"name": "Unauthorized Workspace"}'
   ```
   - Expected: 401 Unauthorized, "Missing authorization" error

2. **Missing Required Name Field**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"description": "No name provided"}'
   ```
   - Expected: 400 Bad Request, "Workspace name required" error

3. **Duplicate Workspace Name (if enforced)**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Duplicate Name"}'
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Duplicate Name"}'
   ```
   - Expected: 400/409 Conflict, "Workspace name already exists" error

---

### **6. GET /v1/workspaces**

**Happy Path Cases:**

1. **Get User Workspaces**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, array of user's workspaces with pagination

2. **Get Workspaces with Pagination**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces?page=1&limit=5" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, paginated results with 5 workspaces max

3. **Empty Workspaces List (New User)**
   ```powershell
   # Login as new user with no workspaces
   $newUserLogin = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "New User", "email": "newuser@test.com", "password": "Pass123!"}'
   $newToken = $newUserLogin.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method GET -Headers @{Authorization="Bearer $newToken"}
   ```
   - Expected: 200 OK, empty workspaces array

**Failure Cases:**

1. **Unauthorized Request**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method GET
   ```
   - Expected: 401 Unauthorized, "Missing authorization" error

2. **Invalid Token**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method GET -Headers @{Authorization="Bearer invalid_token"}
   ```
   - Expected: 422 Unprocessable Entity, "Invalid token" error

3. **Invalid Pagination Parameters**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces?page=-1&limit=0" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 400 Bad Request, "Invalid pagination parameters" error

---

### **7. GET /v1/workspaces/{workspace_id}**

**Happy Path Cases:**

1. **Get Existing Workspace**
   ```powershell
   $workspace = Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Test Workspace"}'
   $workspaceId = $workspace.id
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, full workspace details returned

2. **Get Workspace with Detailed Info**
   ```powershell
   # After adding files/threads to workspace
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, workspace with file_count and thread_count

3. **Access Own Workspace**
   ```powershell
   # Verify user can only access their own workspaces
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 200 OK, workspace details for authorized user

**Failure Cases:**

1. **Non-existent Workspace ID**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/507f1f77bcf86cd799439011" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 404 Not Found, "Workspace not found" error

2. **Invalid Workspace ID Format**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/invalid_id_format" -Method GET -Headers @{Authorization="Bearer $token"}
   ```
   - Expected: 400 Bad Request, "Invalid workspace ID format" error

3. **Access Another User's Workspace**
   ```powershell
   # Create workspace with user1, try to access with user2
   $user2Login = Invoke-RestMethod -Uri "http://localhost:5000/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "User2", "email": "user2@test.com", "password": "Pass123!"}'
   $user2Token = $user2Login.tokens.access_token
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId" -Method GET -Headers @{Authorization="Bearer $user2Token"}
   ```
   - Expected: 403 Forbidden, "Access denied" error

---

## 🧵 **Thread APIs**

### **8. POST /v1/threads**

**Happy Path Cases:**

1. **Create Basic Thread**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "'$workspaceId'", "title": "My First Thread"}'
   ```
   - Expected: 201 Created, thread object with ID returned

2. **Create Thread with Description**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "'$workspaceId'", "title": "Detailed Thread", "description": "This thread has a description"}'
   ```
   - Expected: 201 Created, thread with title and description

3. **Create Multiple Threads in Same Workspace**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "'$workspaceId'", "title": "Thread 1"}'
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "'$workspaceId'", "title": "Thread 2"}'
   ```
   - Expected: 201 Created for both, different thread IDs

**Failure Cases:**

1. **Missing Workspace ID**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"title": "Thread without workspace"}'
   ```
   - Expected: 400 Bad Request, "Workspace ID required" error

2. **Invalid Workspace ID**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "invalid_id", "title": "Thread"}'
   ```
   - Expected: 400 Bad Request, "Invalid workspace ID" error

3. **Access to Other User's Workspace**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $user2Token"} -Body '{"workspace_id": "'$workspaceId'", "title": "Unauthorized thread"}'
   ```
   - Expected: 403 Forbidden, "Access denied to workspace" error

---

## 💬 **Message APIs**

### **9. POST /v1/threads/{thread_id}/messages**

**Happy Path Cases:**

1. **Send Basic Message**
   ```powershell
   $thread = Invoke-RestMethod -Uri "http://localhost:5000/v1/threads" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"workspace_id": "'$workspaceId'", "title": "Chat Thread"}'
   $threadId = $thread.id
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "Hello, what is machine learning?", "type": "user"}'
   ```
   - Expected: 201 Created, message sent and AI response generated

2. **Send Message with File Context**
   ```powershell
   # After uploading files to workspace
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "What does the uploaded document say about AI?", "type": "user", "use_rag": true}'
   ```
   - Expected: 201 Created, AI response with RAG context from files

3. **Conversation Flow**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "What is Python?", "type": "user"}'
   Start-Sleep -Seconds 2
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "Can you give me an example?", "type": "user"}'
   ```
   - Expected: 201 Created for both, AI maintains conversation context

**Failure Cases:**

1. **Invalid Thread ID**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/invalid_thread_id/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "Hello", "type": "user"}'
   ```
   - Expected: 404 Not Found, "Thread not found" error

2. **Empty Message Content**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"content": "", "type": "user"}'
   ```
   - Expected: 400 Bad Request, "Message content required" error

3. **Access Other User's Thread**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/threads/$threadId/messages" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $user2Token"} -Body '{"content": "Unauthorized message", "type": "user"}'
   ```
   - Expected: 403 Forbidden, "Access denied to thread" error

---

## 📁 **File Management APIs**

### **10. POST /v1/workspaces/{workspace_id}/files**

**Happy Path Cases:**

1. **Upload Text File**
   ```powershell
   $textContent = "This is a sample text file for testing the upload functionality."
   $textContent | Out-File -FilePath "test.txt" -Encoding UTF8
   $form = @{
       file = Get-Item "test.txt"
       description = "Test text file"
   }
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form
   ```
   - Expected: 201 Created, file uploaded and processed

2. **Upload PDF File**
   ```powershell
   # Assuming test.pdf exists
   $form = @{
       file = Get-Item "test.pdf"
       description = "Test PDF document"
   }
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form
   ```
   - Expected: 201 Created, PDF processed and vectorized

3. **Upload Multiple Files**
   ```powershell
   # Upload multiple files in sequence
   $form1 = @{ file = Get-Item "doc1.txt"; description = "First document" }
   $form2 = @{ file = Get-Item "doc2.txt"; description = "Second document" }
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form1
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form2
   ```
   - Expected: 201 Created for both, files processed separately

**Failure Cases:**

1. **No File Provided**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -ContentType "multipart/form-data"
   ```
   - Expected: 400 Bad Request, "No file provided" error

2. **Unsupported File Type**
   ```powershell
   $executableContent = @(0x4D, 0x5A)  # MZ header for executable
   $executableContent | Set-Content "test.exe" -Encoding Byte
   $form = @{ file = Get-Item "test.exe" }
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form
   ```
   - Expected: 400 Bad Request, "Unsupported file type" error

3. **File Too Large (if size limits enforced)**
   ```powershell
   # Create a large file (assuming 50MB limit)
   $largeContent = "A" * 52428800  # 50MB+ of text
   $largeContent | Out-File "large.txt"
   $form = @{ file = Get-Item "large.txt" }
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files" -Method POST -Headers @{Authorization="Bearer $token"} -Form $form
   ```
   - Expected: 413 Payload Too Large, "File size exceeds limit" error

---

## 🔍 **Search & Retrieval APIs**

### **11. POST /v1/workspaces/{workspace_id}/files/search**

**Happy Path Cases:**

1. **Basic Text Search**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "machine learning", "limit": 5}'
   ```
   - Expected: 200 OK, relevant file chunks returned

2. **Semantic Search with Context**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "How do neural networks work?", "limit": 10, "include_metadata": true}'
   ```
   - Expected: 200 OK, semantically similar content with metadata

3. **Search with Filters**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "Python programming", "file_types": ["txt", "pdf"], "limit": 5}'
   ```
   - Expected: 200 OK, filtered search results by file type

**Failure Cases:**

1. **Empty Search Query**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$workspaceId/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "", "limit": 5}'
   ```
   - Expected: 400 Bad Request, "Search query required" error

2. **Invalid Workspace for Search**
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/invalid_id/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "test search", "limit": 5}'
   ```
   - Expected: 404 Not Found, "Workspace not found" error

3. **Search in Empty Workspace**
   ```powershell
   $emptyWorkspace = Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"name": "Empty Workspace"}'
   Invoke-RestMethod -Uri "http://localhost:5000/v1/workspaces/$($emptyWorkspace.id)/files/search" -Method POST -ContentType "application/json" -Headers @{Authorization="Bearer $token"} -Body '{"query": "anything", "limit": 5}'
   ```
   - Expected: 200 OK, empty results array

---

## 📊 **Test Execution Strategy**

### **Pre-Test Setup Commands:**
```powershell
# Clear any existing test data
$baseUrl = "http://localhost:5000"

# Register fresh test users
$user1 = Invoke-RestMethod -Uri "$baseUrl/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "Test User 1", "email": "testuser1@example.com", "password": "TestPass123!"}'
$user2 = Invoke-RestMethod -Uri "$baseUrl/v1/auth/register" -Method POST -ContentType "application/json" -Body '{"name": "Test User 2", "email": "testuser2@example.com", "password": "TestPass123!"}'

$token1 = $user1.tokens.access_token
$token2 = $user2.tokens.access_token

# Create test files
"Machine learning is a subset of artificial intelligence." | Out-File "ml_basics.txt"
"Python is a programming language widely used in data science." | Out-File "python_guide.txt"
```

### **Post-Test Cleanup Commands:**
```powershell
# Clean up test files
Remove-Item "test.txt", "ml_basics.txt", "python_guide.txt", "test.exe", "large.txt" -ErrorAction SilentlyContinue

# Note: Database cleanup should be handled by backend test utilities
```

### **Expected Response Times:**
- Authentication APIs: < 500ms
- Workspace/Thread APIs: < 300ms  
- File Upload: < 5s (depending on file size)
- Search APIs: < 2s
- Message APIs: < 10s (includes AI processing)

### **Rate Limiting Tests:**
```powershell
# Test rate limiting on registration endpoint
for ($i = 1; $i -le 10; $i++) {
    try {
        Invoke-RestMethod -Uri "$baseUrl/v1/auth/register" -Method POST -ContentType "application/json" -Body "{`"name`": `"User$i`", `"email`": `"spam$i@test.com`", `"password`": `"Pass123!`"}"
    } catch {
        Write-Output "Rate limit hit at request $i: $($_.Exception.Message)"
    }
}
```

---

## 🎯 **Test Results Template**

### **Test Execution Log:**
```
Date: [DATE]
Tester: [NAME]
Environment: Development
Backend Version: [VERSION]
Frontend Version: [VERSION]

Results:
[ ] Authentication APIs (24 tests)
    [ ] Registration (6 tests)
    [ ] Login (6 tests)  
    [ ] Get User (6 tests)
    [ ] Refresh Token (6 tests)

[ ] Workspace APIs (18 tests)
    [ ] Create Workspace (6 tests)
    [ ] List Workspaces (6 tests)
    [ ] Get Workspace (6 tests)

[ ] Thread APIs (6 tests)
    [ ] Create Thread (6 tests)

[ ] Message APIs (6 tests)  
    [ ] Send Message (6 tests)

[ ] File APIs (6 tests)
    [ ] Upload Files (6 tests)

[ ] Search APIs (6 tests)
    [ ] Search Files (6 tests)

Total Tests: 66
Passed: [COUNT]
Failed: [COUNT] 
Success Rate: [PERCENTAGE]%
```

### **Issue Tracking:**
- **Critical Issues:** [List any blocking issues]
- **Minor Issues:** [List any non-blocking issues]
- **Performance Issues:** [List any response time violations]
- **Recommendations:** [Suggestions for improvement]

---

## 🔧 **Automated Test Script**

For easier execution, this PowerShell script runs all tests:

```powershell
# RAG Chatbot Integration Test Runner
param(
    [string]$BaseUrl = "http://localhost:5000",
    [switch]$CleanupOnly
)

# Test configuration
$ErrorCount = 0
$SuccessCount = 0
$TestResults = @()

function Write-TestResult {
    param($TestName, $Success, $Message = "")
    if ($Success) {
        Write-Host "✅ $TestName" -ForegroundColor Green
        $global:SuccessCount++
    } else {
        Write-Host "❌ $TestName - $Message" -ForegroundColor Red  
        $global:ErrorCount++
    }
    $global:TestResults += @{Name=$TestName; Success=$Success; Message=$Message}
}

function Test-API {
    param($Uri, $Method, $Body, $Headers, $TestName)
    try {
        $response = Invoke-RestMethod -Uri $Uri -Method $Method -Body $Body -Headers $Headers -ContentType "application/json"
        Write-TestResult $TestName $true
        return $response
    } catch {
        Write-TestResult $TestName $false $_.Exception.Message
        return $null
    }
}

# Add full test execution logic here...
# This would include all the test cases from above

Write-Host "Integration Test Results:"
Write-Host "Passed: $SuccessCount"
Write-Host "Failed: $ErrorCount"
Write-Host "Success Rate: $([math]::Round($SuccessCount/($SuccessCount+$ErrorCount)*100,2))%"
```

---

This comprehensive test plan ensures thorough validation of all RAG Chatbot API endpoints with realistic scenarios for both success and failure cases.
