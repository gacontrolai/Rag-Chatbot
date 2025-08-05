import React from 'react';
import { render } from '@testing-library/react';

// Mock the entire API service to avoid axios import issues
jest.mock('./services/api', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
}));

jest.mock('./services/apiService', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
  },
  workspaceService: {
    createWorkspace: jest.fn(),
    getWorkspaces: jest.fn(),
  },
}));

// Simple component test
import App from './App';

test('renders without crashing', () => {
  const { container } = render(<App />);
  // Just check that the app renders without throwing an error
  expect(container).toBeTruthy();
});

test('contains main app element', () => {
  const { container } = render(<App />);
  const appElement = container.querySelector('.App');
  expect(appElement).toBeInTheDocument();
});
