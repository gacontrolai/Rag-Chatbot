import React, { useState, useEffect, useRef } from 'react';
import { threadService, messageService, fileService } from '../services/apiService';
import { Send, Plus, MessageSquare, User, Bot, Upload, FileText, X, Menu, Paperclip } from 'lucide-react';

const ChatInterface = ({ workspaceId }) => {
  const [threads, setThreads] = useState([]);
  const [currentThread, setCurrentThread] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [files, setFiles] = useState([]);
  const [showFileUpload, setShowFileUpload] = useState(false);
  const [uploading, setUploading] = useState(false);
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchFiles = async () => {
    try {
      const response = await fileService.getFiles(workspaceId);
      setFiles(response);
    } catch (err) {
      console.error('Failed to fetch files:', err);
    }
  };

  const fetchThreads = async () => {
    setLoading(true);
    try {
      const response = await threadService.getThreads();
      // Filter threads by workspace if the API supports it
      const workspaceThreads = response.filter(thread => 
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
      setMessages(response);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch messages');
    }
  };

  const createNewThread = async () => {
    try {
      const newThread = await threadService.createThread({
        workspace_id: workspaceId,
        title: `New Chat - ${new Date().toLocaleString()}`,
        description: 'Q&A session about uploaded files'
      });
      
      setThreads([newThread, ...threads]);
      setCurrentThread(newThread);
      setMessages([]);
      setError(null);
    } catch (err) {
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
              <h4>Knowledge Base ({files.length})</h4>
              <button onClick={triggerFileUpload} className="upload-btn" disabled={uploading}>
                <Upload size={14} />
                {uploading ? 'Uploading...' : 'Upload'}
              </button>
            </div>
            <div className="files-list">
              {files.slice(0, 5).map((file) => (
                <div key={file.id} className="file-item">
                  <FileText size={14} />
                  <div className="file-info">
                    <span className="file-name">{file.filename}</span>
                    <span className="file-size">{formatFileSize(file.size)}</span>
                  </div>
                </div>
              ))}
              {files.length > 5 && (
                <div className="file-item more-files">
                  <span>+{files.length - 5} more files</span>
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
                        <div className="message-text">{message.content}</div>
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

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileUpload}
        accept=".txt,.md,.pdf,.doc,.docx"
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
    </div>
  );
};

export default ChatInterface;
