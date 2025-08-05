import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { WorkspaceProvider } from './context/WorkspaceContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Workspace from './pages/Workspace';
import PublicChat from './pages/PublicChat';
import './styles/App.css';

function App() {
  return (
    <AuthProvider>
      <WorkspaceProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/" element={<PublicChat />} />
              <Route path="/chat" element={<PublicChat />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/workspace/:workspaceId" element={<Workspace />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </Router>
      </WorkspaceProvider>
    </AuthProvider>
  );
}

export default App;
