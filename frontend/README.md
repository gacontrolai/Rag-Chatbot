# RAG Chatbot Frontend

React-based frontend application for the RAG Chatbot system.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Environment Configuration

Create a `.env` file:
```env
REACT_APP_API_BASE_URL=http://localhost:5000
```

## Features

- **User Authentication**: Secure login/register with JWT
- **Workspace Management**: Create and manage document workspaces
- **File Upload**: Drag-and-drop file upload with progress tracking
- **Chat Interface**: Real-time chat with AI about uploaded documents
- **Semantic Search**: Search through uploaded content
- **Responsive Design**: Works on desktop, tablet, and mobile

## Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Lint code
- `npm run format` - Format code with Prettier

## Dependencies

- **React 18** - Frontend framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Lucide React** - Icon library

## Project Structure

```
src/
├── components/     # Reusable UI components
├── pages/          # Page components
├── services/       # API integration
├── context/        # React context providers
├── styles/         # CSS stylesheets
└── utils/          # Utility functions
```

## API Integration

This frontend integrates with the RAG Chatbot backend API. See the main project documentation for complete API details.

## Development

For detailed setup instructions, see the main project documentation at the repository root.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
