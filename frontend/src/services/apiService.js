import api from './api';

// Authentication APIs
export const authService = {
  register: async (userData) => {
    const response = await api.post('/v1/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const response = await api.post('/v1/auth/login', credentials);
    const { access_token, refresh_token } = response.data;
    
    // Store tokens
    localStorage.setItem('accessToken', access_token);
    localStorage.setItem('refreshToken', refresh_token);
    
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },

  getCurrentUser: async () => {
    const response = await api.get('/v1/auth/me');
    return response.data;
  },

  refreshToken: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    const response = await api.post('/v1/auth/refresh', {
      refresh_token: refreshToken
    });
    return response.data;
  }
};

// Workspace APIs
export const workspaceService = {
  createWorkspace: async (workspaceData) => {
    const response = await api.post('/v1/workspaces', workspaceData);
    return response.data;
  },

  getWorkspaces: async () => {
    const response = await api.get('/v1/workspaces');
    return response.data;
  },

  getWorkspace: async (workspaceId) => {
    const response = await api.get(`/v1/workspaces/${workspaceId}`);
    return response.data;
  },

  getWorkspaceThreads: async (workspaceId) => {
    const response = await api.get(`/v1/workspaces/${workspaceId}/threads`);
    return response.data;
  }
};

// Thread APIs
export const threadService = {
  createThread: async (threadData) => {
    const response = await api.post('/v1/threads', threadData);
    return response.data;
  },

  getThreads: async () => {
    const response = await api.get('/v1/threads');
    return response.data;
  },

  getThread: async (threadId) => {
    const response = await api.get(`/v1/threads/${threadId}`);
    return response.data;
  },

  updateThread: async (threadId, threadData) => {
    const response = await api.patch(`/v1/threads/${threadId}`, threadData);
    return response.data;
  },

  deleteThread: async (threadId) => {
    const response = await api.delete(`/v1/threads/${threadId}`);
    return response.data;
  }
};

// Message APIs
export const messageService = {
  sendMessage: async (threadId, messageData) => {
    const response = await api.post(`/v1/threads/${threadId}/messages`, messageData);
    return response.data;
  },

  getMessages: async (threadId) => {
    const response = await api.get(`/v1/threads/${threadId}/messages`);
    return response.data;
  }
};

// File Management APIs
export const fileService = {
  uploadFile: async (workspaceId, formData) => {
    const response = await api.post(`/v1/workspaces/${workspaceId}/files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getFiles: async (workspaceId) => {
    const response = await api.get(`/v1/workspaces/${workspaceId}/files`);
    return response.data;
  },

  getFile: async (fileId) => {
    const response = await api.get(`/v1/files/${fileId}`);
    return response.data;
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/v1/files/${fileId}`);
    return response.data;
  },

  searchFiles: async (workspaceId, searchData) => {
    const response = await api.post(`/v1/workspaces/${workspaceId}/files/search`, searchData);
    return response.data;
  },

  getSupportedFormats: async (workspaceId) => {
    const response = await api.get(`/v1/workspaces/${workspaceId}/files/supported-formats`);
    return response.data;
  }
};
