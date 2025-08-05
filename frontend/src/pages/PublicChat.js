import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Send, Bot, User, X, Paperclip, LogIn, UserPlus } from 'lucide-react';
import Header from '../components/Header';

const PublicChat = () => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const simulateAIResponse = (userMessage) => {
    // Simple simulated AI responses for demo purposes
    const responses = [
      "I understand you're asking about that topic. To provide more accurate answers based on your specific documents, please consider uploading your files or signing in to create a workspace.",
      "That's an interesting question! With uploaded documents, I could give you much more detailed and relevant answers. Would you like to sign up to access the full features?",
      "I can help with general questions, but for specific information from your documents, you'll need to upload files to a workspace. Sign in to get started!",
      "Good question! To provide answers based on your specific content and maintain conversation history, please consider creating an account.",
      "I'd be happy to help! For the most accurate responses based on your documents and to save our conversation, please sign in or create an account."
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setSending(true);
    const userMessage = newMessage;
    setNewMessage('');

    // Add user message immediately
    const userMsgObj = {
      id: Date.now(),
      content: userMessage,
      role: 'user',
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsgObj]);

    // Simulate AI response after a short delay
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        content: simulateAIResponse(userMessage),
        role: 'assistant',
        created_at: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiResponse]);
      setSending(false);
    }, 1000 + Math.random() * 2000); // Random delay between 1-3 seconds
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // For non-authenticated users, just show a message about signing up
    setError("To upload files and get AI responses based on your documents, please sign in or create an account.");
    event.target.value = '';
  };

  const triggerFileUpload = () => {
    if (!isAuthenticated) {
      setError("File upload requires an account. Please sign in or register to upload your documents.");
      return;
    }
    fileInputRef.current?.click();
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const handleSignIn = () => {
    navigate('/login');
  };

  const handleSignUp = () => {
    navigate('/register');
  };

  return (
    <div className="public-chat">
      <Header />
      
      <div className="chat-layout">
        {/* Info Sidebar */}
        <div className="info-sidebar">
          <div className="info-content">
            <h3>🤖 AI Chatbot Demo</h3>
            <p>Try out our AI assistant! For full features including:</p>
            
            <ul className="features-list">
              <li>📄 Upload your documents</li>
              <li>💾 Save conversation history</li>
              <li>🔍 Search through your files</li>
              <li>🏢 Create workspaces</li>
              <li>📚 Build knowledge bases</li>
            </ul>
            
            <div className="auth-buttons">
              <button onClick={handleSignIn} className="btn-primary">
                <LogIn size={16} />
                Sign In
              </button>
              <button onClick={handleSignUp} className="btn-secondary">
                <UserPlus size={16} />
                Sign Up
              </button>
            </div>

            <div className="demo-note">
              <h4>Demo Mode</h4>
              <p>You're currently in demo mode. Responses are simulated. Sign in for real AI-powered answers based on your documents!</p>
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="chat-main">
          <div className="chat-header">
            <h2>🚀 Try Our AI Assistant</h2>
            <p>Ask any question to see how it works!</p>
          </div>

          <div className="chat-container">
            <div className="messages-area">
              {messages.length === 0 ? (
                <div className="chat-welcome">
                  <div className="welcome-content">
                    <Bot size={48} />
                    <h1>Hello! How can I help you today?</h1>
                    <p>Try asking me anything to see how the AI assistant works</p>
                    <div className="example-questions">
                      <h4>Example questions you can try:</h4>
                      <div className="question-chips">
                        <button 
                          className="question-chip"
                          onClick={() => setNewMessage("What can you help me with?")}
                        >
                          What can you help me with?
                        </button>
                        <button 
                          className="question-chip"
                          onClick={() => setNewMessage("How does document upload work?")}
                        >
                          How does document upload work?
                        </button>
                        <button 
                          className="question-chip"
                          onClick={() => setNewMessage("Tell me about your features")}
                        >
                          Tell me about your features
                        </button>
                      </div>
                    </div>
                  </div>
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
                  {sending && (
                    <div className="message-wrapper assistant">
                      <div className="message-avatar">
                        <div className="bot-avatar">
                          <Bot size={16} />
                        </div>
                      </div>
                      <div className="message-content">
                        <div className="typing-indicator">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="input-area">
              <div className="input-container">
                <div className="input-wrapper">
                  <button 
                    onClick={triggerFileUpload}
                    className="attach-btn"
                    title="Upload files (requires account)"
                  >
                    <Paperclip size={18} />
                  </button>
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type your message here..."
                    disabled={sending}
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
                    disabled={sending || !newMessage.trim()} 
                    className="send-btn"
                  >
                    <Send size={18} />
                  </button>
                </div>
              </div>
              <div className="input-hint">
                This is a demo. Sign in to upload documents and get AI responses based on your files.
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

export default PublicChat;
