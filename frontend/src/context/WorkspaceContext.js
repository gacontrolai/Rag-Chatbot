import React, { createContext, useContext, useReducer, useCallback } from 'react';
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
  const fetchWorkspaces = useCallback(async () => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      console.log('Fetching workspaces...');
      const workspaces = await workspaceService.getWorkspaces();
      console.log('Workspaces response:', workspaces);
      // Ensure workspaces is always an array
      const workspacesArray = Array.isArray(workspaces) ? workspaces : [];
      console.log('Setting workspaces:', workspacesArray);
      dispatch({ type: WORKSPACE_ACTIONS.SET_WORKSPACES, payload: workspacesArray });
    } catch (error) {
      console.error('Error fetching workspaces:', error);
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.error?.message || error.response?.data?.message || 'Failed to fetch workspaces' 
      });
    }
  }, []);

  // Create workspace
  const createWorkspace = useCallback(async (workspaceData) => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      console.log('Creating workspace with data:', workspaceData);
      const newWorkspace = await workspaceService.createWorkspace(workspaceData);
      console.log('Created workspace:', newWorkspace);
      dispatch({ type: WORKSPACE_ACTIONS.ADD_WORKSPACE, payload: newWorkspace });
      // Refresh the workspace list to ensure consistency
      await fetchWorkspaces();
      return newWorkspace;
    } catch (error) {
      console.error('Error creating workspace:', error);
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.error?.message || error.response?.data?.message || 'Failed to create workspace' 
      });
      throw error;
    }
  }, [fetchWorkspaces]);

  // Set current workspace
  const setCurrentWorkspace = useCallback(async (workspaceId) => {
    dispatch({ type: WORKSPACE_ACTIONS.SET_LOADING, payload: true });
    try {
      console.log('Fetching workspace details for ID:', workspaceId);
      const workspace = await workspaceService.getWorkspace(workspaceId);
      console.log('Workspace details:', workspace);
      dispatch({ type: WORKSPACE_ACTIONS.SET_CURRENT_WORKSPACE, payload: workspace });
    } catch (error) {
      console.error('Error fetching workspace:', error);
      dispatch({ 
        type: WORKSPACE_ACTIONS.SET_ERROR, 
        payload: error.response?.data?.error?.message || error.response?.data?.message || 'Failed to fetch workspace' 
      });
    }
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    dispatch({ type: WORKSPACE_ACTIONS.CLEAR_ERROR });
  }, []);

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
