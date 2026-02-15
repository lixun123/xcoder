# Contributing to XCoder

Thank you for your interest in contributing to XCoder! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)
- [Community Guidelines](#community-guidelines)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Either Ollama or ZhipuAI API access
- Familiarity with command-line interfaces

### Finding Ways to Contribute

- 🐛 **Bug Reports**: Help us find and fix bugs
- 💡 **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve documentation and examples
- 🧪 **Testing**: Write tests or test new features
- 💻 **Code**: Implement new features or fix bugs

Check our [Issues](https://github.com/your-username/xcoder/issues) for:
- `good first issue` - Great for newcomers
- `help wanted` - Issues where we'd appreciate community help
- `documentation` - Documentation improvements needed

## Development Setup

1. **Fork the repository**
   ```bash
   # Visit https://github.com/your-username/xcoder and click 'Fork'
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/xcoder.git
   cd xcoder
   ```

3. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate

   # Install in development mode
   pip install -e .

   # Install development dependencies
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy environment template
   cp .env .env.local

   # Edit .env.local with your configuration
   # Add your API keys and preferred settings
   ```

5. **Verify installation**
   ```bash
   xcoder --version
   xcoder --help
   ```

## Making Changes

### Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

2. **Make your changes**
   - Write clean, readable code
   - Follow our coding standards
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Run the application
   xcoder

   # Test both modes
   xcoder --mode chat
   xcoder --mode debug

   # Test different configurations
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

### Commit Message Convention

We follow [Conventional Commits](https://conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```bash
feat: add support for GPT-4 model
fix: resolve chat history loading issue
docs: update installation instructions
refactor: simplify agent initialization
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guidelines
- Use meaningful variable and function names
- Add docstrings for classes and functions
- Keep functions focused and small
- Use type hints where appropriate

### Code Organization

```python
# Example function with proper documentation
def initialize_agent(model_name: str, base_url: str) -> EntryAgent:
    """
    Initialize an AI agent with the specified configuration.

    Args:
        model_name (str): Name of the model to use
        base_url (str): Base URL for the AI service

    Returns:
        EntryAgent: Initialized agent instance

    Raises:
        ConnectionError: If unable to connect to the AI service
    """
    # Implementation here
    pass
```

### File Structure

- Keep related functionality together
- Use meaningful module and package names
- Avoid circular imports
- Place utility functions in appropriate modules

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_agents.py

# Run with coverage
python -m pytest --cov=xcoder
```

### Writing Tests

- Write tests for new features
- Include both positive and negative test cases
- Test edge cases and error conditions
- Use descriptive test names

Example:
```python
def test_entry_agent_initialization():
    """Test that EntryAgent initializes correctly with valid parameters."""
    agent = EntryAgent(model_name="test-model", base_url="http://localhost")
    assert agent.model_name == "test-model"
    assert agent.base_url == "http://localhost"

def test_entry_agent_invalid_url():
    """Test that EntryAgent raises error with invalid URL."""
    with pytest.raises(ValueError):
        EntryAgent(model_name="test-model", base_url="invalid-url")
```

## Submitting Changes

### Pull Request Process

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature
   git rebase main
   ```

2. **Push your changes**
   ```bash
   git push origin feature/your-feature
   ```

3. **Create Pull Request**
   - Go to GitHub and create a Pull Request
   - Use a descriptive title
   - Fill out the PR template completely
   - Link related issues

### Pull Request Guidelines

- **Title**: Use a descriptive title that summarizes the change
- **Description**: Explain what changed and why
- **Testing**: Describe how you tested your changes
- **Documentation**: Update docs if needed
- **Breaking Changes**: Clearly mark any breaking changes

### PR Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
- [ ] Tested manually
- [ ] Added automated tests
- [ ] All existing tests pass

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated if needed
- [ ] No breaking changes (or clearly documented)
```

## Reporting Bugs

### Before Submitting

1. Check [existing issues](https://github.com/your-username/xcoder/issues)
2. Try with the latest version
3. Check if it's a configuration issue

### Bug Report Template

```markdown
## Bug Description
A clear description of the bug

## Steps to Reproduce
1. Run command '...'
2. Enter input '...'
3. See error

## Expected Behavior
What you expected to happen

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.0]
- XCoder version: [e.g., 1.0.0]
- AI Provider: [e.g., Ollama, ZhipuAI]

## Additional Context
Any other relevant information
```

## Suggesting Features

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature

## Use Case
Why would this feature be useful?

## Proposed Solution
How should this feature work?

## Alternatives Considered
Other ways to achieve the same goal

## Additional Context
Any other relevant information
```

## Community Guidelines

### Communication

- Be respectful and inclusive
- Provide constructive feedback
- Help newcomers get started
- Share knowledge and experiences

### Getting Help

- 💬 **Discussions**: Use GitHub Discussions for questions
- 🐛 **Issues**: Report bugs via GitHub Issues
- 📖 **Wiki**: Check our Wiki for additional documentation

### Recognition

Contributors are recognized in:
- Release notes
- Contributors section
- Special mentions for significant contributions

## Development Tips

### Debugging

- Use the `--verbose` flag for detailed logging
- Test with different AI providers
- Test both chat and debug modes
- Check configuration files

### Performance

- Profile code for performance bottlenecks
- Optimize for common use cases
- Consider memory usage with large conversations

### Documentation

- Update docstrings for new functions
- Add examples for new features
- Update CLI help text if needed
- Keep README.md current

## Release Process

For maintainers:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. Create release branch
4. Test thoroughly
5. Merge to main
6. Tag release
7. Update documentation

## Questions?

If you have questions not covered here:
- Check existing [Issues](https://github.com/your-username/xcoder/issues)
- Start a [Discussion](https://github.com/your-username/xcoder/discussions)
- Contact the maintainers

Thank you for contributing to XCoder! 🚀