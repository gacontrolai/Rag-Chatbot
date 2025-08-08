import React, { useState, useEffect, useRef } from 'react';
import { threadService, messageService, fileService } from '../services/apiService';
import { Send, Plus, MessageSquare, User, Bot, Upload, FileText, X, Menu, Paperclip, ChevronRight, ExternalLink, Trash2, AlertTriangle } from 'lucide-react';

const ChatInterface = ({ workspaceId }) => {
  const [threads, setThreads] = useState([]);
  const [currentThread, setCurrentThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [referencesOpen, setReferencesOpen] = useState(true);
  const [currentReferences, setCurrentReferences] = useState({});
  const [files, setFiles] = useState([]);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [deletingFile, setDeletingFile] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchThreads();
    fetchFiles();
  }, [workspaceId]);

  useEffect(() => {
    if (currentThread) {
      fetchMessages(currentThread.id);
    }
  }, [currentThread]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to extract references from assistant messages
  const extractReferencesFromMessages = (messages) => {
    const latestReferences = {};
    
    messages.forEach(message => {
      if (message.role === 'assistant' && message.content.trim().startsWith('{')) {
        try {
          const parsed = JSON.parse(message.content);
          if (parsed.references) {
            Object.assign(latestReferences, parsed.references);
          }
        } catch (e) {
          // Ignore parsing errors
        }
      }
    });
    
    return latestReferences;
  };

  // Update references when messages change
  useEffect(() => {
    const references = extractReferencesFromMessages(messages);
    setCurrentReferences(references);
  }, [messages]);

  // Helper function to clean RAG context from user messages
  const cleanMessageContent = (content, role) => {
    if (role !== 'user') {
      // For assistant messages, parse JSON response and extract clean text
      if (role === 'assistant' && content.trim().startsWith('{')) {
        try {
          const parsed = JSON.parse(content);
          if (parsed.response) {
            // Return clean response without reference tags
            return parsed.response.replace(/<ref id='[^']*'>/g, '').replace(/<\/ref>/g, '');
          }
        } catch (e) {
          console.warn('Failed to parse AI response JSON:', e);
        }
      }
      return content;
    }
    
    // For user messages, remove RAG context
    const ragContextRegex = /<RAG_CONTEXT>[\s\S]*?<\/RAG_CONTEXT>/gi;
    const cleanContent = content.replace(ragContextRegex, '');
    
    // Extract the actual user message after "User:" prefix
    const userMatch = cleanContent.match(/User:\s*(.+)$/);
    if (userMatch) {
      return userMatch[1].trim();
    }
    
    // Fallback: return content without RAG context
    return cleanContent.replace(/^\s*\n+/, '').trim();
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchFiles = async () => {
    try {
      const response = await fileService.getFiles(workspaceId);
      setFiles(response.files || []);
    } catch (err) {
      console.error('Failed to fetch files:', err);
      setFiles([]);
    }
  };

  const fetchThreads = async () => {
    setLoading(true);
    try {
      const response = await threadService.getThreads();
      const threads_data = response.threads || response;
      // Filter threads by workspace if the API supports it
      const workspaceThreads = threads_data.filter(thread => 
        thread.workspace_id === workspaceId
      );
      setThreads(workspaceThreads);
      
      // Auto-select the first thread if available
      if (workspaceThreads.length > 0 && !currentThread) {
        setCurrentThread(workspaceThreads[0]);
      }
      
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch threads');
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (threadId) => {
    try {
      const response = await messageService.getMessages(threadId);
      const messages_data = response.messages || response;
      setMessages(messages_data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch messages');
    }
  };

  const createNewThread = async () => {
    try {
      const response = await threadService.createThread({
        workspace_id: workspaceId,
        title: `New Chat - ${new Date().toLocaleString()}`,
        description: 'Q&A session about uploaded files'
      });
      
      // Backend returns {thread: {...}}, so we need response.thread
      const newThread = response.thread;
      console.log('New thread created:', newThread);
      
      setThreads([newThread, ...threads]);
      setCurrentThread(newThread);
      setMessages([]);
      setError(null);
    } catch (err) {
      console.error('Failed to create thread:', err);
      setError(err.response?.data?.message || 'Failed to create thread');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !currentThread) return;

    setSending(true);
    const userMessage = newMessage;
    setNewMessage('');

    // Add user message to UI immediately
    const tempUserMessage = {
      id: Date.now(),
      content: userMessage,
      role: 'user',
      created_at: new Date().toISOString()
    };

    try {
      setMessages(prev => [...prev, tempUserMessage]);

      // Send message to API
      const response = await messageService.sendMessage(currentThread.id, {
        content: userMessage,
        role: 'user'
      });

      // Refresh messages to get the complete conversation including bot response
      await fetchMessages(currentThread.id);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to send message');
      // Remove the temporary message on error
      setMessages(prev => prev.filter(msg => msg.id !== tempUserMessage.id));
    } finally {
      setSending(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await fileService.uploadFile(workspaceId, formData);
      await fetchFiles(); // Refresh the file list
      setShowFileUpload(false);
      
      // Reset the input
      event.target.value = '';
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleDeleteFile = async (fileId, fileName) => {
    setDeletingFile(fileId);
    try {
      await fileService.deleteFile(fileId);
      await fetchFiles(); // Refresh the file list
      setError(null);
      setShowDeleteConfirm(null);
    } catch (err) {
      setError(err.response?.data?.message || `Failed to delete ${fileName}`);
    } finally {
      setDeletingFile(null);
    }
  };

  const confirmDelete = (file) => {
    setShowDeleteConfirm(file);
  };

  const cancelDelete = () => {
    setShowDeleteConfirm(null);
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="gpt-interface">
      {/* Sidebar */}
      <div className={`gpt-sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <button onClick={createNewThread} className="new-chat-btn">
            <Plus size={16} />
            New chat
          </button>
        </div>
        
        <div className="threads-list">
          {threads.map((thread) => (
            <div
              key={thread.id}
              className={`thread-item ${currentThread?.id === thread.id ? 'active' : ''}`}
              onClick={() => setCurrentThread(thread)}
            >
              <MessageSquare size={16} />
              <span className="thread-title">{thread.title}</span>
            </div>
          ))}
        </div>

        {/* File Upload Section */}
        <div className="sidebar-footer">
          <div className="files-section">
            <div className="files-header">
              <h4>Knowledge Base ({Array.isArray(files) ? files.length : 0})</h4>
              <button onClick={triggerFileUpload} className="upload-btn" disabled={uploading}>
                <Upload size={14} />
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            <div className="files-list">
              {Array.isArray(files) && files.slice(0, 5).map((file) => (
                <div key={file.id} className="file-item">
                  <div className="file-icon">
                    <FileText size={14} />
                  </div>
                  <div className="file-info">
                    <span className="file-name" title={file.filename}>{file.filename}</span>
                    <span className="file-size">{formatFileSize(file.size)}</span>
                  </div>
                  <div className="file-actions">
                    <button
                      onClick={() => confirmDelete(file)}
                      className="delete-file-btn"
                      disabled={deletingFile === file.id}
                      title={`Delete ${file.filename}`}
                    >
                      {deletingFile === file.id ? (
                        <div className="spinner-small"></div>
                      ) : (
                        <Trash2 size={12} />
                      )}
                    </button>
                  </div>
                </div>
              ))}
              {Array.isArray(files) && files.length > 5 && (
                <div className="file-item more-files">
                  <span>+{files.length - 5} more files</span>
                  <button className="view-all-btn">View All</button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="gpt-main">
        <div className="chat-header">
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)} 
            className="sidebar-toggle"
          >
            <Menu size={20} />
          </button>
          <h2>{currentThread?.title || 'Select a conversation'}</h2>
          <div style={{ marginLeft: 'auto', display: 'flex', gap: '8px' }}>
            <button 
              onClick={() => setReferencesOpen(!referencesOpen)}
              className="sidebar-toggle"
              title="Toggle References Panel"
            >
              <FileText size={18} />
            </button>
          </div>
        </div>

        <div className="chat-container">
          {!currentThread ? (
            <div className="chat-welcome">
              <div className="welcome-content">
                <h1>How can I help you today?</h1>
                <p>Ask questions about your uploaded documents</p>
              </div>
            </div>
          ) : (
            <div className="messages-area">
              {messages.length === 0 ? (
                <div className="empty-conversation">
                  <Bot size={32} />
                  <p>Start a conversation about your documents</p>
                </div>
              ) : (
                <div className="messages">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`message-wrapper ${message.role}`}
                    >
                      <div className="message-avatar">
                        {message.role === 'user' ? (
                          <div className="user-avatar">
                            <User size={16} />
                          </div>
                        ) : (
                          <div className="bot-avatar">
                            <Bot size={16} />
                          </div>
                        )}
                      </div>
                      <div className="message-content">
                        <div className="message-text">
                          {cleanMessageContent(message.content, message.role)}
                        </div>
                        <div className="message-time">
                          {formatTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  ))}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>
          )}

          {/* Input Area */}
          <div className="input-area">
            <div className="input-container">
              <div className="input-wrapper">
                <button 
                  onClick={triggerFileUpload}
                  className="attach-btn"
                  disabled={uploading}
                >
                  <Paperclip size={18} />
                </button>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Message..."
                  disabled={sending || !currentThread}
                  className="message-input"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage(e);
                    }
                  }}
                />
                <button 
                  onClick={sendMessage} 
                  disabled={sending || !newMessage.trim() || !currentThread} 
                  className="send-btn"
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* References Panel */}
      <div className={`references-panel ${referencesOpen ? '' : 'hidden'}`}>
        <div className="references-header">
          <h3>References</h3>
          <button 
            onClick={() => setReferencesOpen(!referencesOpen)}
            className="references-toggle"
          >
            <ChevronRight size={16} style={{ transform: referencesOpen ? 'rotate(180deg)' : 'rotate(0deg)' }} />
          </button>
        </div>
        
        <div className="references-content">
          {Object.keys(currentReferences).length === 0 ? (
            <div className="references-empty">
              <FileText size={32} />
              <h4>No References Yet</h4>
              <p>References will appear here when the AI uses information from your documents to answer questions.</p>
            </div>
          ) : (
            <div className="references-list">
              <div className="references-info">
                <span>{Object.keys(currentReferences).length} reference{Object.keys(currentReferences).length !== 1 ? 's' : ''} found</span>
              </div>
              {Object.entries(currentReferences).map(([id, ref]) => (
                <div key={id} className="reference-item">
                  <div className="reference-header">
                    <div className="reference-title">
                      <FileText size={16} />
                      <span className="reference-filename">{ref.title || id}</span>
                    </div>
                    <ExternalLink size={12} className="reference-external" />
                  </div>
                  <div className="reference-content">
                    <div className="reference-text">
                      "{ref.text}"
                    </div>
                    {ref.line && (
                      <div className="reference-metadata">
                        <span className="reference-location">Line {ref.line}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileUpload}
        accept=".txt,.csv,.docx"
        style={{ display: 'none' }}
      />

      {error && (
        <div className="error-toast">
          <span>{error}</span>
          <button onClick={() => setError(null)}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="delete-modal">
            <div className="modal-header">
              <AlertTriangle size={24} className="warning-icon" />
              <h3>Delete File</h3>
            </div>
            <div className="modal-body">
              <p>Are you sure you want to delete <strong>"{showDeleteConfirm.filename}"</strong>?</p>
              <p className="warning-text">This action cannot be undone. The file will be permanently removed from your knowledge base.</p>
            </div>
            <div className="modal-actions">
              <button onClick={cancelDelete} className="cancel-btn">
                Cancel
              </button>
              <button 
                onClick={() => handleDeleteFile(showDeleteConfirm.id, showDeleteConfirm.filename)} 
                className="delete-btn"
                disabled={deletingFile === showDeleteConfirm.id}
              >
                {deletingFile === showDeleteConfirm.id ? (
                  <>
                    <div className="spinner-small"></div>
                    Deleting...
                  </>
                ) : (
                  <>
                    <Trash2 size={16} />
                    Delete
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatInterface;
