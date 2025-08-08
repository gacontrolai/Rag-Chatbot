import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { User, LogOut, Settings, Brain, Home, Briefcase, Sparkles } from 'lucide-react';

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogin = () => {
    navigate('/login');
  };

  const handleRegister = () => {
    navigate('/register');
  };

  const handleLogout = () => {
    logout();
    setShowUserMenu(false);
    navigate('/'); // Navigate to public chat after logout
  };

  const toggleUserMenu = () => {
    setShowUserMenu(!showUserMenu);
  };

  return (
    <header className="app-header">
      <div className="header-container">
        <div className="header-left">
          <div className="logo" onClick={() => navigate('/')}>
            <div className="logo-icon">
              <Brain size={28} />
              <Sparkles size={14} className="logo-sparkle" />
            </div>
            <div className="logo-text">
              <span className="logo-main">IntelliDoc</span>
              <span className="logo-sub">AI Assistant</span>
            </div>
          </div>
          
          <nav className="nav-links">
            {!isAuthenticated && (
              <button 
                onClick={() => navigate('/')} 
                className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
              >
                <Home size={16} />
                <span>Chat</span>
              </button>
            )}
            
            {isAuthenticated && (
              <button 
                onClick={() => navigate('/dashboard')} 
                className={`nav-link ${location.pathname === '/dashboard' ? 'active' : ''}`}
              >
                <Briefcase size={16} />
                <span>Dashboard</span>
              </button>
            )}
          </nav>
        </div>

        <div className="header-right">
          {isAuthenticated ? (
            <div className="user-menu-container">
              <button onClick={toggleUserMenu} className="user-avatar">
                <div className="user-avatar-circle">
                  <User size={18} />
                </div>
                <span className="user-name">{user?.username || user?.email}</span>
              </button>
              
              {showUserMenu && (
                <div className="user-dropdown">
                  <div className="user-info">
                    <div className="user-email">{user?.email}</div>
                  </div>
                  <div className="dropdown-divider"></div>
                  <button onClick={() => setShowUserMenu(false)} className="dropdown-item">
                    <Settings size={16} />
                    Settings
                  </button>
                  <button onClick={handleLogout} className="dropdown-item logout">
                    <LogOut size={16} />
                    Log out
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="auth-buttons">
              <button onClick={handleLogin} className="btn-outline">
                Log in
              </button>
              <button onClick={handleRegister} className="btn-primary">
                Sign up
              </button>
            </div>
          )}
        </div>
      </div>
      
      {/* Overlay to close dropdown when clicking outside */}
      {showUserMenu && (
        <div 
          className="dropdown-overlay" 
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </header>
  );
};

export default Header;
