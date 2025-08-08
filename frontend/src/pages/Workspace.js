import React, { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useWorkspace } from '../context/WorkspaceContext';
import { useAuth } from '../context/AuthContext';
import ChatInterface from '../components/ChatInterface';
import Header from '../components/Header';
import { Lock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Workspace = () => {
  const { workspaceId } = useParams();
  const { currentWorkspace, setCurrentWorkspace, loading, error } = useWorkspace();
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const lastFetchedIdRef = useRef(null);

  useEffect(() => {
    if (workspaceId && isAuthenticated && lastFetchedIdRef.current !== workspaceId) {
      console.log('Fetching workspace:', workspaceId);
      lastFetchedIdRef.current = workspaceId;
      setCurrentWorkspace(workspaceId);
    }
  }, [workspaceId, setCurrentWorkspace, isAuthenticated]);

  const handleLoginPrompt = () => {
    navigate('/login');
  };

  if (!isAuthenticated) {
    return (
      <div className="workspace">
        <Header />
        <main className="workspace-main">
          <div className="auth-required">
            <Lock size={48} />
            <h2>Sign in required</h2>
            <p>You need to sign in to access workspaces and upload files.</p>
            <button onClick={handleLoginPrompt} className="btn-primary">
              Sign in
            </button>
          </div>
        </main>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="workspace">
        <Header />
        <div className="loading">Loading workspace...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="workspace">
        <Header />
        <div className="error-message">{error}</div>
      </div>
    );
  }

  if (!currentWorkspace) {
    return (
      <div className="workspace">
        <Header />
        <div className="error-message">Workspace not found</div>
      </div>
    );
  }

  return (
    <div className="workspace">
      <Header />
      <main className="workspace-main">
        <ChatInterface workspaceId={workspaceId} />
      </main>
    </div>
  );
};

export default Workspace;
