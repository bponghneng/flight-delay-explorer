# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Flight Delay Explorer is a Python CLI tool that processes airline on-time performance data from the AviationStack API. It's designed as a learning project focused on Python fundamentals, CLI tooling, API integration, and Test-Driven Development (TDD).

## Development Commands

### Package Management
This project uses `uv` for dependency management:

```bash
# Install dependencies (including dev dependencies)
uv sync --group dev

# Install the package in development mode
pip install -e .

# Run the application
uv run main.py --flight-date 2025-06-01
```

### Code Quality Tools
```bash
# Format code with Ruff
uv run ruff format src tests

# Run linting with Ruff
uv run ruff check src tests

# Type checking with MyPy (strict mode for src/)
uv run mypy src/ --strict
uv run mypy tests/

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/flight_delay_explorer tests/

# Run specific test types
uv run pytest -m unit
uv run pytest -m integration
```

### Git Hooks
Git hooks are located in `.githooks/` and must be activated once after cloning:

```bash
git config core.hooksPath .githooks
```

- **pre-commit**: Runs Ruff formatting/linting, MyPy type checking, and file integrity checks
- **pre-push**: Runs full test suite with 90% coverage requirement

## Architecture

### Core Components

The application follows a layered architecture with clear separation of concerns:

**CLI Layer** (`src/flight_delay_explorer/cli.py`)
- Typer-based command interface
- Rich table formatting for output
- Error handling and user feedback
- Progress indicators for long-running operations

**API Layer** (`src/flight_delay_explorer/api/client.py`)
- AviationStack API integration using httpx
- Retry logic with exponential backoff
- Rate limiting and error handling
- Response parsing to internal models

**Data Models** (`src/flight_delay_explorer/models.py`)
- `FlightRecord`: Core data structure for flight information
- `DelayCategory`: Enum for flight delay classifications
- `QueryParams`: API query parameters

**Configuration** (`src/flight_delay_explorer/config.py`)
- Pydantic-based settings management
- Environment variable loading with `.env` support
- Type-safe configuration with validation

**Utilities**
- `utils/logging.py`: Centralized logging setup
- `parsers/data_parser.py`: JSON data parsing utilities

### Data Flow
1. CLI command receives flight date parameter
2. Configuration loaded from environment variables
3. API client makes request to AviationStack with retries
4. Response parsed into FlightRecord objects
5. Data displayed in formatted Rich table
6. Optional save to JSON file

### Delay Classification Logic
Flights are classified into categories based on arrival delay:
- On time: ≤15 minutes
- Minor delay: 16-60 minutes  
- Major delay: 61-180 minutes
- Severe delay: >180 minutes
- Special cases: Cancelled, Diverted

## Testing Strategy

### TDD Approach
This project strictly follows Test-Driven Development:
1. Write failing test first
2. Implement minimal code to pass test
3. Refactor while maintaining test passes

### Test Structure
- **Unit tests**: Individual component testing (`test_*.py`)
- **Integration tests**: Component interaction testing (`test_integration.py`)
- **CLI tests**: Command-line interface testing (`test_cli.py`)

### Coverage Requirements
- Minimum 90% test coverage enforced by pre-push hooks
- Tests should be deterministic and fast
- Use mocking for external dependencies (API calls)

### Test Utilities
- Use `typer.testing.CliRunner` for CLI testing
- Mock HTTP requests with `pytest-httpx` or `respx`
- Test fixtures in `tests/fixtures/` directory

## Configuration

### Environment Variables
Required environment variables (see `.env.example`):
- `AVIATIONSTACK_ACCESS_KEY`: AviationStack API key
- Optional: `BASE_URL`, `MAX_RETRIES`, `TIMEOUT_SECONDS`

### API Limitations
- Free tier only allows queries for current date
- Rate limiting requires retry logic with backoff
- API returns limited fields; some parsing is defensive

## Development Workflow

### Branch Strategy
- Feature branches: `feature/description`
- Bug fixes: `fix/description`  
- Documentation: `docs/description`
- Chores: `chore/description`

### Commit Format
Follow conventional commit format:
```
<type>: <description>

Types: feat, fix, docs, style, refactor, test, chore
```

### Code Quality Standards
- Use type hints for all function signatures
- Follow PEP 8 style guidelines (enforced by Ruff)
- Keep functions small and focused (<20 lines when possible)
- Write docstrings for public functions and classes
- Prefer composition over inheritance

## Key Implementation Details

### Error Handling Strategy
- Specific exception types for different error scenarios
- Rich console output for user-friendly error messages
- Comprehensive logging with context
- Graceful degradation for non-critical failures

### API Client Design
- Built-in retry logic for transient failures
- Exponential backoff for rate limiting
- Proper timeout handling
- Request/response logging for debugging

### CLI Design Principles
- Clear, colored output using Rich library
- Progress indicators for long operations
- Helpful error messages with hints
- Optional verbose logging levels

## Project History

This project was built using specification-driven development with AI assistance. The comprehensive implementation plan in `specs/core-package-structure.md` demonstrates the TDD approach taken throughout development. The project successfully executed the complete specification in a single iteration, validating the specification-first methodology.
