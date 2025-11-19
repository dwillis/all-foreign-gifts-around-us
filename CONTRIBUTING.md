# Contributing to Foreign Gifts Tracker

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment for all contributors

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/all-foreign-gifts-around-us.git`
3. Follow the [Setup Guide](docs/setup.md) to configure your development environment
4. Create a new branch for your feature: `git checkout -b feature/your-feature-name`

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Virtual environment tool (venv or pipenv)

### Install Development Dependencies

```bash
pip install -r requirements.txt
```

This includes testing and code quality tools.

### Pre-commit Checks

Before committing, ensure your code passes:

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/

# Run tests
pytest tests/
```

## Project Structure

```
src/
├── extractors/     # LLM-based data extraction modules
├── processors/     # Data processing and transformation
├── database/       # Database management
├── api/           # External API clients
└── utils/         # Shared utilities

tests/             # Test files mirroring src/ structure
docs/              # Documentation
config/            # Configuration files
data/              # Data directories (not committed)
```

## Making Changes

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use type hints

Example:

```python
def extract_donor_info(donor_text: str) -> Dict[str, str]:
    """
    Extract structured donor information from text.

    Args:
        donor_text: Raw donor text from Federal Register

    Returns:
        Dictionary with keys: name, title, country
    """
    # Implementation
    pass
```

### Testing

- Write tests for all new features
- Maintain or improve test coverage
- Use pytest for testing
- Place tests in `tests/` directory mirroring `src/` structure

Example test:

```python
def test_extract_donor_info():
    donor_text = "His Excellency John Doe, Prime Minister of Example Country"
    result = extract_donor_info(donor_text)

    assert result["name"] == "John Doe"
    assert result["title"] == "Prime Minister"
    assert result["country"] == "Example Country"
```

### Documentation

- Update README.md if adding user-facing features
- Add docstrings to all new functions/classes
- Update relevant docs in `docs/` directory
- Include usage examples

## Types of Contributions

### Bug Fixes

1. Search existing issues to avoid duplicates
2. Create an issue describing the bug if one doesn't exist
3. Reference the issue in your PR

### New Features

1. Open an issue to discuss the feature first
2. Get feedback from maintainers
3. Implement the feature
4. Add tests and documentation
5. Submit a PR

### Documentation

- Fix typos, improve clarity
- Add examples
- Update outdated information
- Translate to other languages

### Data Quality

- Report extraction errors
- Suggest improvements to prompts
- Identify edge cases

## Pull Request Process

1. **Update your branch** with the latest main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Ensure all checks pass**:
   - Tests pass
   - Code is formatted
   - No linting errors
   - Documentation is updated

3. **Write a clear PR description**:
   - What does this PR do?
   - Why is this change needed?
   - How was it tested?
   - Any breaking changes?
   - Related issues?

4. **Respond to feedback**:
   - Address reviewer comments
   - Make requested changes
   - Re-request review when ready

5. **Squash commits** if requested:
   ```bash
   git rebase -i HEAD~n  # where n is number of commits
   ```

## Commit Messages

Write clear, descriptive commit messages:

```
Add feature to extract gift values in multiple currencies

- Parse currency symbols and codes
- Convert to USD using historical rates
- Add tests for currency conversion
- Update documentation

Fixes #123
```

Format:
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed description if needed
- Reference related issues

## Issue Reporting

### Bug Reports

Include:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version)
- Error messages/logs
- Sample data if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case / why it's needed
- Proposed implementation (optional)
- Alternatives considered

## Development Workflow

### Working with Data

- **Never commit large data files** (CSV, JSON, DB files)
- Use sample/test data in `tests/fixtures/`
- Add data file patterns to `.gitignore`

### API Keys

- **Never commit API keys**
- Use environment variables or config files (gitignored)
- Use example config files with placeholder values

### Testing Locally

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_extractors.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v
```

## Code Review Guidelines

### For Authors

- Keep PRs focused and reasonably sized
- Respond promptly to feedback
- Be open to suggestions
- Update PR based on comments

### For Reviewers

- Be constructive and kind
- Explain reasoning behind suggestions
- Approve when satisfied
- Test the changes if possible

## Questions?

- Open an issue for questions
- Tag with "question" label
- Check existing issues/discussions first

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in README.md contributors section
- Credited in commit history

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!
