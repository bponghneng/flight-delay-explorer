# Contributing to Flight Delay Explorer

Thank you for your interest in contributing to Flight Delay Explorer! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Git Workflow](#git-workflow)
- [Branch Naming Conventions](#branch-naming-conventions)
- [Commit Message Format](#commit-message-format)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Testing Requirements](#testing-requirements)
- [Code Quality Standards](#code-quality-standards)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/your-username/flight-delay-explorer.git
   cd flight-delay-explorer
   ```
3. Install dependencies:
   ```bash
   uv sync --group dev
   ```
4. Run tests to ensure everything works:
   ```bash
   uv run pytest
   ```

## Development Setup

This project uses `uv` for dependency management and includes several development tools:

- **Ruff**: Code formatting and linting
- **MyPy**: Type checking
- **Pytest**: Testing framework
- **Coverage**: Test coverage reporting

### Git Hooks

This project uses custom Git hooks located in the `.githooks/` directory:

- **pre-commit**: Runs code quality checks including Ruff linting/formatting, MyPy type checking, file integrity checks, merge conflict detection, and debug statement detection
- **pre-push**: Installs the package in development mode and runs the full test suite with coverage checks

#### Activating Git Hooks

After cloning the repository, you must run the following command once to configure Git to use the custom hooks directory:

```bash
git config core.hooksPath .githooks
```

This step is necessary for the hooks to run automatically when you commit or push code, ensuring code quality standards are maintained.

### Running Development Tools

```bash
# Format code
uv run ruff format src tests

# Run linter
uv run ruff check src tests

# Type checking
uv run mypy src tests

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/flight_delay_explorer tests/
```

## Git Workflow

We use a feature branch workflow:

1. **Create a feature branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code quality standards

3. **Commit your changes** using conventional commit format

4. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub

6. **Address review feedback** if needed

7. **Merge** once approved (typically done by maintainers)

### Branch Types

- **Feature branches**: `feature/description` - New functionality
- **Bug fix branches**: `fix/description` - Bug fixes
- **Documentation branches**: `docs/description` - Documentation updates
- **Chore branches**: `chore/description` - Maintenance tasks

## Branch Naming Conventions

Use descriptive, kebab-case branch names:

- `feature/add-flight-filtering`
- `fix/api-timeout-handling`
- `docs/update-installation-guide`
- `chore/update-dependencies`
- `test/improve-parser-coverage`

## Commit Message Format

We follow a simplified version of the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>: <description>

[optional body]

[optional footer(s)]
```

### Types

- **feat**: A new feature for the user
- **fix**: A bug fix for the user
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries
- **build**: Changes that affect the build system or external dependencies
- **ci**: Changes to CI configuration files and scripts

### Examples

```bash
feat: add flight delay filtering option
fix: handle timeout errors in API client
docs: update README with installation instructions
test: add tests for edge case handling
refactor: simplify flight record structure
chore: update dependencies to latest versions
```

## Pull Request Process

1. **Ensure your branch is up to date** with main:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Run all quality checks** locally:
   ```bash
   uv run ruff format src tests
   uv run ruff check src tests --fix
   uv run mypy src tests
   uv run pytest --cov=src/flight_delay_explorer tests/
   ```

3. **Push your changes** and create a Pull Request

4. **Fill out the PR template** completely

5. **Ensure all CI checks pass**

6. **Respond to review feedback** promptly

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage is at least 90%
- [ ] Code follows formatting standards (Ruff)
- [ ] No linting errors (Ruff)
- [ ] Type checking passes (MyPy)
- [ ] PR description explains the changes
- [ ] Related issues are linked

## Code Review Guidelines

### For Contributors

- **Keep PRs focused** - One feature/fix per PR
- **Write clear descriptions** - Explain what and why
- **Test your changes** - Include tests for new functionality
- **Be responsive** - Address feedback quickly
- **Be open to feedback** - Remember we're all learning

### For Reviewers

- **Be constructive** - Provide specific, actionable feedback
- **Be timely** - Review PRs within 2-3 business days
- **Check functionality** - Verify the changes work as intended
- **Verify tests** - Ensure adequate test coverage
- **Consider maintainability** - Think about long-term code health

## Testing Requirements

- **Unit tests** are required for all new functionality
- **Integration tests** should be added for API interactions
- **Test coverage** must be at least 90%
- **Tests should be deterministic** - No flaky tests
- **Use descriptive test names** - Tests should serve as documentation

### Test Structure

```python
def test_should_do_something_when_condition():
    # Arrange
    setup_test_data()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected_value
```

## Code Quality Standards

### Python Style

- Follow **PEP 8** style guidelines
- Use **type hints** for all function signatures
- Write **docstrings** for public functions and classes
- Prefer **composition over inheritance**
- Use **meaningful variable names**

### Code Organization

- Keep functions **small and focused** (< 20 lines when possible)
- Use **early returns** to reduce nesting
- **Separate concerns** - each module should have a single responsibility
- **Avoid deep nesting** - prefer guard clauses

### Error Handling

- Use **specific exception types**
- **Log errors** with appropriate context
- **Fail fast** - validate inputs early
- **Provide helpful error messages**

### Documentation

- **README** should be up to date
- **API documentation** for public interfaces
- **Inline comments** for complex logic
- **Type hints** serve as documentation

## Questions?

If you have any questions about contributing, please:

1. Check existing [GitHub Issues](https://github.com/your-username/flight-delay-explorer/issues)
2. Create a new issue with the `question` label
3. Reach out to the maintainers

Thank you for contributing to Flight Delay Explorer! 🛫
