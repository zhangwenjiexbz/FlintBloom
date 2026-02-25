# Contributing to FlintBloom

Thank you for your interest in contributing to FlintBloom! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/zhangwenjiexbz/FlintBloom.git
cd FlintBloom
```

### 2. Set Up Development Environment

```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Frontend setup (optional)
cd ../frontend
npm install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Backend Development

```bash
# Run the application
cd backend
python -m app.main

# Run tests
pytest

# Run tests with coverage
pytest --cov=app --cov-report=html

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Frontend Development

```bash
cd frontend
npm run dev  # Start development server
npm run build  # Build for production
```

### Database Migrations

When you modify database models:

```bash
# Create migration (if using Alembic)
alembic revision --autogenerate -m "Description of changes"

# Apply migration
alembic upgrade head
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Write docstrings for public functions/classes
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `isort` for import sorting

Example:
```python
from typing import List, Optional

def get_checkpoints(
    thread_id: str,
    limit: int = 50,
    offset: int = 0
) -> List[Checkpoint]:
    """
    Get checkpoints for a thread.

    Args:
        thread_id: Thread identifier
        limit: Maximum number of checkpoints
        offset: Number of checkpoints to skip

    Returns:
        List of checkpoint objects
    """
    pass
```

### TypeScript/React

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Use meaningful component and variable names

## Testing

### Writing Tests

```python
# backend/test_feature.py
import pytest
from app.modules.offline.parser import CheckpointParser

def test_checkpoint_parser():
    """Test checkpoint parsing"""
    parser = CheckpointParser()
    # Your test code here
    assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest test_main.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app
```

## Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are clear

### 2. Commit Messages

Use conventional commit format:

```
feat: add checkpoint comparison API
fix: resolve database connection timeout
docs: update installation instructions
test: add tests for parser module
refactor: simplify adapter factory
```

### 3. Submit PR

1. Push your branch to your fork
2. Open a Pull Request on GitHub
3. Fill out the PR template
4. Link any related issues
5. Wait for review

### 4. PR Review

- Address reviewer feedback
- Keep PR focused and small
- Update documentation as needed
- Ensure CI passes

## Project Structure

```
FlintBloom/
├── backend/
│   ├── app/
│   │   ├── core/           # Configuration, database
│   │   ├── db/             # Models, schemas, adapters
│   │   ├── modules/        # Feature modules
│   │   │   ├── offline/    # Offline analysis
│   │   │   └── realtime/   # Real-time tracking
│   │   └── main.py         # Application entry
│   ├── tests/              # Test files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   └── package.json
└── docs/                   # Documentation
```

## Adding New Features

### Backend Feature

1. Create module in `app/modules/`
2. Add models in `app/db/models.py`
3. Add schemas in `app/db/schemas.py`
4. Create API router
5. Register router in `app/main.py`
6. Add tests
7. Update documentation

### Frontend Feature

1. Create component in `src/components/`
2. Add types in `src/types/`
3. Add API calls in `src/services/`
4. Update routing if needed
5. Add tests
6. Update documentation

## Database Adapters

When adding support for a new database:

1. Create adapter in `app/db/adapters/`
2. Inherit from `BaseDatabaseAdapter`
3. Implement required methods
4. Add to `AdapterFactory`
5. Update configuration
6. Add tests
7. Update documentation

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Update API documentation
- Add examples for new features

## Questions?

- Open an issue for discussion
- Join our community chat (if available)
- Check existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to FlintBloom! 🌸
