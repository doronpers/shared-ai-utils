# Contributing to Shared AI Utils

Thank you for your interest in contributing to Shared AI Utils! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Git

### Setup Steps

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/shared-ai-utils.git
   cd shared-ai-utils
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**

   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks (optional)**

   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Making Changes

1. **Create a branch**

   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**

   - Follow the coding standards (see below)
   - Write tests for new features
   - Update documentation as needed

3. **Run tests and linting**

   ```bash
   # Run tests
   pytest

   # Format code
   black src/ tests/

   # Lint code
   ruff check src/ tests/

   # Type checking
   mypy src/
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

   Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test additions/changes
   - `refactor:` for code refactoring
   - `chore:` for maintenance tasks

5. **Push and create a pull request**

   ```bash
   git push origin feature/your-feature-name
   ```

   Then create a pull request on GitHub.

## Coding Standards

### Python Style

- **Formatter**: `black` (line-length: 100)
- **Linter**: `ruff`
- **Type Hints**: Required for all public functions and methods
- **Style**: `snake_case` for functions/vars, `PascalCase` for classes

### Code Quality

- **Type Hints**: Use type hints for all public APIs
- **Docstrings**: Include docstrings for all public functions and classes
- **Tests**: Aim for >80% code coverage
- **Validation**: Use Pydantic models for data validation

### Example

```python
from typing import Optional
from pydantic import BaseModel

class MyConfig(BaseModel):
    """Configuration for my feature."""

    api_key: str
    timeout: Optional[int] = 30

def process_data(config: MyConfig) -> dict:
    """
    Process data using the provided configuration.

    Args:
        config: Configuration object

    Returns:
        Dictionary with processed results
    """
    # Implementation
    return {}
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/shared_ai_utils --cov-report=html

# Run specific test file
pytest tests/unit/test_llm.py

# Run specific test
pytest tests/unit/test_llm.py::test_llm_manager
```

### Writing Tests

- Place tests in `tests/unit/` or `tests/integration/`
- Use descriptive test names: `test_feature_should_do_something`
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies

### Example Test

```python
import pytest
from shared_ai_utils.llm import LLMManager

@pytest.mark.asyncio
async def test_llm_manager_generates_response():
    """Test that LLM manager generates a response."""
    # Arrange
    manager = LLMManager(preferred_provider="anthropic")

    # Act
    response = await manager.generate(
        system_prompt="You are helpful",
        user_prompt="Hello",
        max_tokens=10
    )

    # Assert
    assert response.text is not None
    assert len(response.text) > 0
```

## Documentation

### Updating Documentation

- Update `README.md` for user-facing changes
- Add detailed guides to appropriate sections
- Update docstrings for API changes
- Keep examples current

### Documentation Standards

- Use clear, concise language
- Include code examples
- Update version numbers when applicable
- Link to related documentation

## Pull Request Process

1. **Ensure your PR is ready**
   - All tests pass
   - Code is formatted and linted
   - Documentation is updated
   - Commit messages follow conventions

2. **Create the PR**
   - Use a clear, descriptive title
   - Describe what changes you made and why
   - Reference any related issues
   - Add screenshots if applicable

3. **Respond to feedback**
   - Address review comments
   - Make requested changes
   - Keep discussions constructive

## Project Structure

```
shared-ai-utils/
├── src/
│   └── shared_ai_utils/
│       ├── api/          # FastAPI utilities
│       ├── assessment/   # Assessment engine
│       ├── cli/          # CLI framework
│       ├── config/       # Configuration system
│       ├── llm/          # LLM providers
│       ├── patterns/     # Pattern management
│       └── tts/          # Text-to-speech
├── tests/
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
└── pyproject.toml       # Project configuration
```

## Questions?

- Open an issue for bug reports or feature requests
- Check existing issues and discussions
- Review the README for common questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Shared AI Utils! 🎉
