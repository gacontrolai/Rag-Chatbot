import React, { createContext, useContext, useReducer } from 'react';
import { workspaceService } from '../services/apiService';

// Initial state
const initialState = {
  workspaces: [],
  currentWorkspace: null,
  loading: false,
  error: null,
};

// Action types
const WORKSPACE_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_WORKSPACES: 'SET_WORKSPACES',
  SET_CURRENT_WORKSPACE: 'SET_CURRENT_WORKSPACE',
  ADD_WORKSPACE: 'ADD_WORKSPACE',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
const workspaceReducer = (state, action) => {
  switch (action.type) {
    case WORKSPACE_ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    case WORKSPACE_ACTIONS.SET_WORKSPACES:
      return {
        ...state,
        workspaces: action.payload,
        loading: false,
        error: null,
      };
    case WORKSPACE_ACTIONS.SET_CURRENT_WORKSPACE:
      return {
        ...state,
        currentWorkspace: action.payload,
        loading: false,
        error: null,
      };
    case WORKSPACE_ACTIONS.ADD_WORKSPACE:
      return {
        ...state,
        workspaces: [...state.workspaces, action.payload],
        loading: false,
        error: null,
      };
    case WORKSPACE_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case WORKSPACE_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
};

// Create context
const WorkspaceContext = createContext();

// Workspace provider component
export const WorkspaceProvider = ({ children }) => {
  const [state, dispatch] = useReducer(workspaceReducer, initialState);

  // Fetch workspaces
  const fetchWorkspaces = async () => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      const workspaces = await workspaceService.getWorkspaces();
      dispatch({ type: WORKSPACE_ACTIONS.SET_WORKSPACES, payload: workspaces });
    } catch (error) {
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to fetch workspaces' 
      });
    }
  };

  // Create workspace
  const createWorkspace = async (workspaceData) => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      const newWorkspace = await workspaceService.createWorkspace(workspaceData);
      dispatch({ type: WORKSPACE_ACTIONS.ADD_WORKSPACE, payload: newWorkspace });
      return newWorkspace;
    } catch (error) {
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to create workspace' 
      });
      throw error;
    }
  };

  // Set current workspace
  const setCurrentWorkspace = async (workspaceId) => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      const workspace = await workspaceService.getWorkspace(workspaceId);
      dispatch({ type: WORKSPACE_ACTIONS.SET_CURRENT_WORKSPACE, payload: workspace });
    } catch (error) {
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.message || 'Failed to fetch workspace' 
      });
    }
  };

  // Clear error
  const clearError = () => {
    dispatch({ type: WORKSPACE_ACTIONS.CLEAR_ERROR });
  };

  const value = {
    ...state,
    fetchWorkspaces,
    createWorkspace,
    setCurrentWorkspace,
    clearError,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
};

// Custom hook to use workspace context
export const useWorkspace = () => {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
};
