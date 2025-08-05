import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { authService } from '../services/apiService';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  loading: true,
  error: null,
};

// Action types
const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  SET_LOADING: 'SET_LOADING',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        loading: true,
        error: null,
      };
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        isAuthenticated: true,
        loading: false,
        error: null,
      };
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload,
      };
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };
    case AUTH_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        loading: false,
      };
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check for existing token on app load
  useEffect(() => {
    const checkAuth = async () => {
      // For demo purposes, skip API calls if API_BASE_URL is localhost:8000 and server is not running
      const apiBaseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
      
      if (apiBaseUrl.includes('localhost:8000')) {
        // In demo mode, just check for tokens but don't validate with server
        const token = localStorage.getItem('accessToken');
        if (token) {
          try {
            const user = await authService.getCurrentUser();
            dispatch({ type: AUTH_ACTIONS.SET_USER, payload: user });
          } catch (error) {
            console.warn('API server not available, running in demo mode');
            // Clear tokens if server is not available
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      } else {
        // Production mode - validate with server
        const token = localStorage.getItem('accessToken');
        if (token) {
          try {
            const user = await authService.getCurrentUser();
            dispatch({ type: AUTH_ACTIONS.SET_USER, payload: user });
          } catch (error) {
            console.warn('Failed to get current user, clearing tokens:', error.message);
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            dispatch({ type: AUTH_ACTIONS.SET_USER, payload: null });
          }
        } else {
          dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: false });
        }
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    try {
      const response = await authService.login(credentials);
      const user = await authService.getCurrentUser();
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_SUCCESS, 
        payload: { user, ...response } 
      });
      return response;
    } catch (error) {
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_FAILURE, 
        payload: error.response?.data?.message || 'Login failed' 
      });
      throw error;
    }
  };

  // Register function
  const register = async (userData) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START });
    try {
      await authService.register(userData);
      // After successful registration, log the user in
      const response = await authService.login({
        email: userData.email,
        password: userData.password
      });
      const user = await authService.getCurrentUser();
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_SUCCESS, 
        payload: { user, ...response } 
      });
      return response;
    } catch (error) {
      dispatch({ 
        type: AUTH_ACTIONS.LOGIN_FAILURE, 
        payload: error.response?.data?.message || 'Registration failed' 
      });
      throw error;
    }
  };

  // Logout function
  const logout = () => {
    authService.logout();
    dispatch({ type: AUTH_ACTIONS.LOGOUT });
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  };

  const value = {
    ...state,
    login,
    register,
    logout,
    clearError,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
