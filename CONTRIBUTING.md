# Contributing to RAG Chatbot

Thank you for your interest in contributing to the RAG Chatbot project! This document provides guidelines and information for contributors.

## 🤝 Ways to Contribute

- **Bug Reports**: Report issues or bugs you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve documentation and examples
- **Testing**: Help test new features and report issues

## 🚀 Getting Started

### 1. Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Rag-Chatbot.git
cd Rag-Chatbot
```

### 2. Set Up Development Environment
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac: venv\Scripts\activate (Windows)
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### 3. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

## 🛠️ Development Guidelines

### Code Style

#### Python (Backend)
```bash
# Format with Black
black .

# Lint with flake8
flake8

# Type checking (optional)
mypy .
```

#### JavaScript/React (Frontend)
```bash
# Format with Prettier
npm run format

# Lint with ESLint
npm run lint
npm run lint:fix
```

### Naming Conventions

#### Python
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Files/Modules**: `snake_case.py`

#### JavaScript/React
- **Functions/Variables**: `camelCase`
- **Components**: `PascalCase`
- **Files**: `PascalCase.js` for components, `camelCase.js` for utilities
- **Constants**: `UPPER_SNAKE_CASE`

### Project Structure

Follow the established patterns:
- **Backend**: Repository → Service → API pattern
- **Frontend**: Components → Pages → Services pattern
- **Shared**: Keep utilities in dedicated folders

## 📝 Commit Guidelines

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code formatting (no logic changes)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples
```bash
feat(backend): add semantic search for uploaded files
fix(frontend): resolve file upload progress bar issue
docs: update API documentation for new endpoints
refactor(backend): improve embedding service architecture
```

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/ -v
pytest tests/ --cov=. --cov-report=html
```

### Frontend Testing
```bash
cd frontend
npm test
npm run test:coverage
```

### Test Requirements
- **New Features**: Include unit tests
- **Bug Fixes**: Add regression tests
- **Coverage**: Maintain >70% test coverage
- **Integration**: Test API integration points

## 📋 Pull Request Process

### 1. Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No merge conflicts with main branch

### 2. PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### 3. Review Process
1. **Automated Checks**: CI/CD pipeline runs
2. **Code Review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

## 🐛 Bug Reports

### Bug Report Template
```markdown
**Describe the Bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment**
- OS: [e.g., Windows, macOS, Linux]
- Browser: [e.g., Chrome, Firefox]
- Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired feature

**Describe alternatives you've considered**
Alternative solutions or features

**Additional context**
Mockups, examples, or additional context
```

## 🔧 Development Setup Details

### Environment Variables
```bash
# Backend (.env)
SECRET_KEY=dev-secret-key
DEBUG=True
MONGODB_URI=mongodb://localhost:27017/ai_chatbot_dev
OPENAI_API_KEY=your-dev-api-key

# Frontend (.env)
REACT_APP_API_BASE_URL=http://localhost:5000
```

### Database Setup
```bash
# MongoDB (local development)
mongod --dbpath ./data/db

# Or use MongoDB Atlas for cloud development
```

### IDE Configuration

#### VS Code Settings
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "eslint.workingDirectories": ["frontend"]
}
```

## 🚀 Release Process

### Version Numbers
- **Major**: Breaking changes (1.0.0 → 2.0.0)
- **Minor**: New features (1.0.0 → 1.1.0)
- **Patch**: Bug fixes (1.0.0 → 1.0.1)

### Release Checklist
- [ ] Version numbers updated
- [ ] Changelog updated
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Release notes prepared

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Email**: [maintainer-email@example.com]

### Documentation
- **API Docs**: `/docs/API_DOCUMENTATION.md`
- **Setup Guide**: `/docs/SETUP_GUIDE.md`
- **Project Structure**: `/docs/PROJECT_STRUCTURE.md`

## 🙏 Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release Notes**: Acknowledgments
- **GitHub**: Contributor graphs and statistics

## 📋 Code of Conduct

### Our Standards
- **Respectful**: Be kind and respectful to all participants
- **Inclusive**: Welcome people of all backgrounds and identities
- **Collaborative**: Work together constructively
- **Professional**: Maintain professional standards

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information
- Other unprofessional conduct

### Enforcement
Project maintainers will enforce this code of conduct and may remove comments, commits, or contributors who violate these standards.

---

Thank you for contributing to the RAG Chatbot project! Your efforts help make this project better for everyone. 🚀
