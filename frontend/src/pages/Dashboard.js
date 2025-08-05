import React, { useEffect, useState } from 'react';
import { useWorkspace } from '../context/WorkspaceContext';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Plus, MessageSquare, FileText, Users, Lock } from 'lucide-react';
import Header from '../components/Header';

const Dashboard = () => {
  const { workspaces, fetchWorkspaces, createWorkspace, loading, error } = useWorkspace();
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newWorkspaceName, setNewWorkspaceName] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      fetchWorkspaces();
    }
  }, [isAuthenticated]);

  const handleCreateWorkspace = async (e) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }
    
    try {
      await createWorkspace({ 
        name: newWorkspaceName,
        description: `Workspace for ${newWorkspaceName}` 
      });
      setNewWorkspaceName('');
      setShowCreateForm(false);
    } catch (err) {
      // Error is handled in context
    }
  };

  const handleWorkspaceClick = (workspace) => {
    navigate(`/workspace/${workspace.id}`);
  };

  const handleLoginPrompt = () => {
    navigate('/login');
  };

  if (loading && workspaces.length === 0) {
    return (
      <div className="dashboard">
        <Header />
        <div className="loading">Loading...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <Header />

      <main className="dashboard-main">
        <div className="dashboard-content">
          <div className="welcome-section">
            <h1>Welcome to Knowledge Chatbot</h1>
            <p>Upload your documents and chat with AI to find answers quickly</p>
          </div>

          {!isAuthenticated && (
            <div className="guest-notice">
              <div className="notice-content">
                <Lock size={24} />
                <div>
                  <h3>Sign in to access your workspaces</h3>
                  <p>Create an account to save your conversations and upload files</p>
                  <button onClick={handleLoginPrompt} className="btn-primary">
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          )}

          {isAuthenticated && (
            <>
              <div className="section-header">
                <h2>Your Workspaces</h2>
                <button 
                  onClick={() => setShowCreateForm(true)}
                  className="btn-primary"
                >
                  <Plus size={20} />
                  Create Workspace
                </button>
              </div>

              {error && <div className="error-message">{error}</div>}

              <div className="workspaces-grid">
                {workspaces.length === 0 ? (
                  <div className="empty-state">
                    <Users size={48} />
                    <h3>No workspaces yet</h3>
                    <p>Create your first workspace to start uploading files and chatting!</p>
                  </div>
                ) : (
                  workspaces.map((workspace) => (
                    <div 
                      key={workspace.id}
                      className="workspace-card"
                      onClick={() => handleWorkspaceClick(workspace)}
                    >
                      <div className="workspace-icon">
                        <FileText size={24} />
                      </div>
                      <h3>{workspace.name}</h3>
                      <p>{workspace.description || 'No description'}</p>
                      <div className="workspace-stats">
                        <span>
                          <MessageSquare size={16} />
                          {workspace.thread_count || 0} threads
                        </span>
                        <span>
                          <FileText size={16} />
                          {workspace.file_count || 0} files
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </>
          )}

          {/* Demo section for non-authenticated users */}
          {!isAuthenticated && (
            <div className="demo-section">
              <h2>How it works</h2>
              <div className="features-grid">
                <div className="feature-card">
                  <FileText size={32} />
                  <h3>Upload Documents</h3>
                  <p>Upload text files, PDFs, and documents to create your knowledge base</p>
                </div>
                <div className="feature-card">
                  <MessageSquare size={32} />
                  <h3>Ask Questions</h3>
                  <p>Chat with AI about your documents and get instant, accurate answers</p>
                </div>
                <div className="feature-card">
                  <Users size={32} />
                  <h3>Organize Workspaces</h3>
                  <p>Create separate workspaces for different topics or projects</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Modal for creating workspace */}
      {showCreateForm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Create New Workspace</h3>
            <form onSubmit={handleCreateWorkspace}>
              <div className="form-group">
                <label htmlFor="workspaceName">Workspace Name:</label>
                <input
                  type="text"
                  id="workspaceName"
                  value={newWorkspaceName}
                  onChange={(e) => setNewWorkspaceName(e.target.value)}
                  required
                  placeholder="Enter workspace name"
                />
              </div>
              <div className="modal-actions">
                <button type="submit" className="btn-primary">
                  Create
                </button>
                <button 
                  type="button" 
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
