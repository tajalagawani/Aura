# Contributing to Aura

Thank you for your interest in contributing to Aura! This document provides guidelines for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

Open an issue on GitHub with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)

### Suggesting Features

Open an issue tagged "enhancement" with:
- Clear use case
- Proposed API/interface
- Why this benefits the project

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** with clear, documented code
4. **Add tests** for new functionality
5. **Run tests** (`pytest`)
6. **Update documentation** as needed
7. **Commit** with clear messages
8. **Push** to your fork
9. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aura
cd aura

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Run with coverage
pytest --cov=aura --cov-report=html
```

## Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run formatters:
```bash
black aura
isort aura
flake8 aura
mypy aura
```

## Testing

- Write tests for all new functionality
- Aim for 80%+ code coverage
- Use pytest fixtures for common setups
- Test edge cases and error conditions

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_aav.py

# Run with coverage
pytest --cov=aura
```

## Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Update README.md for user-facing changes
- Add examples for new features

## Commit Messages

Use clear, descriptive commit messages:

```
feat: Add caching layer for AAV files
fix: Handle edge case in change detector
docs: Update installation guide
test: Add tests for Guardian validator
```

## Questions?

Open an issue or discussion on GitHub!

Thank you for contributing! 🙏
