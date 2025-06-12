# Core Package Structure Implementation Plan

## Overview
This plan implements the initial CLI foundation for Flight Delay Explorer using test-driven development, starting with the `fetch` command.

## Phase 1: Test-Driven CLI Foundation

### Step 1.1: Create CLI Fetch Command Test
**Goal**: Establish TDD foundation with a failing test for the `fetch` command

**Tasks**:
1. Create `tests/` directory structure:
   ```
   tests/
   ├── __init__.py
   ├── test_cli.py
   └── fixtures/
       └── sample_flight_data.json
   ```

2. Create test for `fetch` command in `tests/test_cli.py`:
   - Test should invoke CLI with `fetch --flight-date 2024-01-01`
   - Verify output contains table with title "Flight Delay Data"
   - Verify table has columns: "Date" (cyan), "Flight" (magenta), "Route" (green), "Delay" (yellow), "Status" (red)
   - Use `typer.testing.CliRunner` for CLI testing
   - Mock data source to return sample flight records

3. Create sample test data in `tests/fixtures/sample_flight_data.json`:
   - Include 3-5 sample flight records from the flight_date download at `data/2025-06-07.json`

4. **Verify test fails**: Run `pytest tests/test_cli.py -v` and confirm failure

### Step 1.2: Implement Minimal CLI Structure
**Goal**: Create basic CLI infrastructure to make test pass

**Tasks**:
1. Create `src/flight_delay_explorer/cli.py`:
   - Import `typer` and `rich` for CLI and formatting
   - Create main `app = typer.Typer()` instance
   - Implement `fetch()` command with `flight_date` parameter
   - Use `rich.table.Table` for colored output formatting
   - Mock data loading for now (use hardcoded sample data)

2. Update `src/flight_delay_explorer/__init__.py`:
   - Expose CLI entry point
   - Set package version

3. Update `main.py`:
   - Import and call CLI app
   - Add proper entry point for CLI execution

4. **Verify test passes**: Run `pytest tests/test_cli.py -v` and confirm success

## Phase 2: Core Package Architecture

### Step 2.1: Create Data Models Tests
**Goal**: Establish TDD foundation with failing tests for core data models

**Tasks**:
1. Create test for data models in `tests/test_models.py`:
   - Test `FlightRecord` dataclass with properties:
     - `arrival_delay` (int, minutes)
     - `destination_icao` (str, airport code)
     - `flight_date` (str, date)
     - `flight_icao` (str, flight identifier)
     - `flight_status` (DelayCategory enum)
     - `origin_icao` (str, airport code)
   - Test `DelayCategory` enum with values:
     - `CANCELLED="cancelled"`
     - `DIVERTED="diverted"`
     - `ON_TIME="on time"`
     - `MAJOR_DELAY="major delay"`
     - `MINOR_DELAY="minor delay"`
     - `SEVERE_DELAY="severe delay"`
   - Test `QueryParams` dataclass with property:
     - `flight_date` (str, date)
   - Include validation tests for data types and enum values
   - Test dataclass instantiation and field access

2. **Verify test fails**: Run `pytest tests/test_models.py -v` and confirm failure

### Step 2.2: Implement Data Models
**Goal**: Create type-safe data structures to make tests pass

**Tasks**:
1. Create `src/flight_delay_explorer/models.py`:
   - Import required modules: `dataclass`, `enum`, typing
   - Define `DelayCategory` enum with specified string values
   - Define `FlightRecord` dataclass with specified properties and type hints
   - Define `QueryParams` dataclass with specified property and type hints
   - Add proper type annotations throughout

2. **Verify test passes**: Run `pytest tests/test_models.py -v` and confirm success

### Step 2.3: Create Configuration Management Tests
**Goal**: Establish TDD foundation with failing tests for configuration system

**Tasks**:
1. Create test for configuration in `tests/test_config.py`:
   - Test `Settings` class using `pydantic.BaseSettings` with properties:
     - `access_key` (str, API key)
     - `base_url` (str, API base URL)
     - `max_retries` (int, retry attempts)
     - `timeout_seconds` (int, request timeout)
   - Test environment variable loading and validation
   - Test default values and overrides
   - Test configuration validation and error handling

2. **Verify test fails**: Run `pytest tests/test_config.py -v` and confirm failure

### Step 2.4: Implement Configuration Management
**Goal**: Create configuration system to make tests pass

**Tasks**:
1. Create `src/flight_delay_explorer/config.py`:
   - Import `pydantic.BaseSettings`
   - Define `Settings` class inheriting from `BaseSettings`
   - Add specified properties with appropriate type hints and default values
   - Configure environment variable loading with proper prefixes
   - Add validation for required fields

2. Create `.env.example`:
   - Document all required environment variables:
     - `FLIGHT_ACCESS_KEY` - AviationStack API access key
     - `FLIGHT_BASE_URL` - API base URL (default: https://api.aviationstack.com/v1)
     - `FLIGHT_MAX_RETRIES` - Maximum retry attempts (default: 3)
     - `FLIGHT_TIMEOUT_SECONDS` - Request timeout in seconds (default: 30)
   - Include example values and descriptions

3. **Verify test passes**: Run `pytest tests/test_config.py -v` and confirm success

## Phase 3: API Client Setup

### Step 3.1: Create Logging Utility Tests
**Goal**: Establish TDD foundation with failing tests for a logging setup utility

**Tasks**:
1. Create test for logging utility in `tests/test_logging.py`:
   - Test creating a logger with different log levels (INFO, DEBUG, ERROR)
   - Test log message formatting with timestamps and levels
   - Test log output destinations (console, file)
   - Test context-specific logging (request IDs, correlation IDs)
   - Test integration with external libraries
   - Include tests for error handling and edge cases

2. **Verify test fails**: Run `pytest tests/test_logging.py -v` and confirm failure

### Step 3.2: Implement Logging Utility
**Goal**: Create robust logging infrastructure to make tests pass

**Tasks**:
1. Create `src/flight_delay_explorer/utils/logging.py`:
   - Import Python's built-in `logging` module
   - Create a `setup_logger()` function that accepts parameters:
     - `name` (str, logger name)
     - `level` (int, log level)
     - `log_file` (Optional[str], file path for logging)
     - `log_format` (Optional[str], custom log format)
   - Configure console and file handlers based on parameters
   - Set appropriate formatting with timestamps and log levels
   - Add support for context variables (request IDs)
   - Implement proper error handling for file access issues

2. **Verify test passes**: Run `pytest tests/test_logging.py -v` and confirm success

### Step 3.3: Create API Client Tests
**Goal**: Establish TDD foundation with failing tests for aviationstack API client

**Tasks**:
1. Create test for API client in `tests/test_api_client.py`:
   - Test connection to aviationstack API `/v1/flights` endpoint
   - Test HTTP request/response cycle with mocked responses
   - Test proper URL construction with query parameters
   - Test authentication header inclusion
   - Test error handling for common HTTP errors (4xx, 5xx)
   - Test retry logic for transient failures
   - Test response parsing and data extraction
   - Test rate limit handling and backoff strategies
   - Use `pytest-httpx` or `responses` library to mock HTTP interactions

2. **Verify test fails**: Run `pytest tests/test_api_client.py -v` and confirm failure

### Step 3.4: Implement API Client
**Goal**: Create reliable API client to make tests pass

**Tasks**:
1. Create `src/flight_delay_explorer/api/client.py`:
   - Import required modules: `httpx`, logging utility, configuration
   - Create `AviationStackClient` class with methods:
     - `__init__(self, settings: Settings, logger=None)`
     - `get_flights(self, params: QueryParams) -> list[FlightRecord]`
   - Implement HTTP request construction with proper headers and authentication
   - Add automatic retry logic with exponential backoff
   - Implement robust error handling and logging
   - Add response validation and parsing to convert API data to `FlightRecord` objects
   - Integrate with the logging utility for request/response logging

2. **Verify test passes**: Run `pytest tests/test_api_client.py -v` and confirm success

## Phase 4: Data Parser

### Step 4.1: Create Data Parser Tests
**Goal**: Establish TDD foundation with failing tests for a data parser utility

**Tasks**:
1. Create test for data parser in `tests/test_data_parser.py`:
   - Test loading and parsing JSON data from file
   - Test converting JSON data to `FlightRecord` objects
   - Test error handling for invalid JSON
   - Test error handling for missing files
   - Test handling of missing or malformed fields
   - Test proper handling of date formats
   - Test mapping of delay information to proper `DelayCategory` values

2. **Verify test fails**: Run `pytest tests/test_data_parser.py -v` and confirm failure

### Step 4.2: Implement Data Parser
**Goal**: Create data parser utility to make tests pass

**Tasks**:
1. Create `src/flight_delay_explorer/parsers/data_parser.py`:
   - Import required modules: `json`, models, logging utility
   - Create `FlightDataParser` class with methods:
     - `__init__(self, logger=None)`
     - `parse_file(self, file_path: str) -> list[FlightRecord]`
   - Implement JSON file loading with proper error handling
   - Add validation for required fields and data types
   - Implement mapping logic to convert API response format to `FlightRecord` objects
   - Integrate with logging utility for debugging and error reporting
   - Handle edge cases like missing fields or invalid data formats

2. **Verify test passes**: Run `pytest tests/test_data_parser.py -v` and confirm success

## Phase 5: CLI Orchestration

### Step 5.1: Update CLI Command Tests
**Goal**: Establish TDD foundation with failing tests for the complete `fetch` command that orchestrates the API client and data parser

**Tasks**:
1. Update tests for `fetch` command in `tests/test_cli.py`:
   - Test CLI integration with the AviationStack API client
     - Verify proper API client initialization with settings
     - Mock API responses and verify correct handling
   - Test proper parsing of API response data
     - Verify conversion of API data to FlightRecord objects
   - Test display of fetched data in formatted table
     - Verify all columns display correctly with proper styling
     - Check pagination for large result sets
   - Test comprehensive logging throughout the process
     - Verify start/end of operations logged
     - Verify API requests/responses logged
     - Verify data processing steps logged
   - Test error handling scenarios:
     - API authentication failures
     - Network connectivity issues
     - Rate limiting responses
     - Malformed API responses
     - Command parameter validation errors
   - Test command option validation
     - Verify date format validation
     - Test required vs optional parameters

2. **Verify test fails**: Run `pytest tests/test_cli.py -v` and confirm failure

### Step 5.2: Implement CLI Orchestration
**Goal**: Create a fully functional `fetch` command that integrates all components

**Tasks**:
1. Update `src/flight_delay_explorer/cli.py`:
   - Import all required components:
     - AviationStackClient from api module
     - Settings from config module
     - Logging utility from utils module
     - FlightRecord and QueryParams from models module
   - Enhance `fetch()` command to:
     - Initialize settings from environment/config files
     - Set up proper logging with command context
     - Create and configure API client with settings
     - Build query parameters from command options
     - Make API request and handle potential errors
     - Process API response into FlightRecord objects
     - Format and display results in Rich table with proper styling
     - Save fetched data to local cache if requested
     - Provide informative error messages for all failure scenarios
   - Add progress indicators for long-running operations
   - Implement proper exit codes for different outcomes

2. **Verify test passes**: Run `pytest tests/test_cli.py -v` and confirm success

### Step 5.3: Integration Testing
**Goal**: Verify all components work together properly in real-world scenarios

**Tasks**:
1. Create integration test in `tests/test_integration.py`:
   - Test end-to-end flow with mocked API responses
   - Verify configuration loading, API client initialization, data fetching, parsing, and display
   - Test with various command line arguments and options
   - Verify proper data saving to local cache files
   - Test error propagation and handling across component boundaries

2. Implement manual testing with real API:
   - Create test script that uses real API credentials
   - Test against real aviationstack API (using limited calls)
   - Verify correct handling of real-world API responses
   - Document any discrepancies between mock tests and real API behavior

3. **Verify tests pass**: Run all test suites and confirm success

## Phase 6: Development Tools Configuration

### Step 6.1: Create Development Tools Configuration Tests
**Goal**: Establish TDD foundation with failing tests for development tools configuration

**Tasks**:
1. Create test for development tools configuration in `tests/test_dev_tools.py`:
   - Test Black code formatting compliance
   - Test Ruff linting rules conformance
   - Test MyPy type checking validation
   - Test Pytest configuration and discovery
   - Test Coverage reporting configuration
   - Include tests to verify config files exist and contain required settings
   - Test integration between tools (e.g., Black formatting doesn't break Ruff rules)

2. **Verify test fails**: Run `pytest tests/test_dev_tools.py -v` and confirm failure

### Step 6.2: Implement Development Tools Configuration
**Goal**: Create comprehensive development tools configuration to make tests pass

**Tasks**:
1. Create `pyproject.toml` with tool configurations:
   - Add `[tool.black]` section with:
     - `line-length = 88`
     - `target-version = ["py39"]`
     - `include = "src/**/*.py"` and `"tests/**/*.py"`
   - Add `[tool.ruff]` section with:
     - Linting rules (E, F, W, I, etc.)
     - Import sorting configuration
     - Line length and target version settings
   - Add `[tool.mypy]` section with:
     - `python_version = "3.9"`
     - `disallow_untyped_defs = true`
     - `disallow_incomplete_defs = true`
     - `check_untyped_defs = true`
     - `disallow_untyped_decorators = true`
     - `no_implicit_optional = true`
     - `strict_optional = true`
   - Add `[tool.pytest.ini_options]` section with:
     - `testpaths = ["tests"]`
     - `python_files = "test_*.py"`
     - `python_functions = "test_*"`
     - `python_classes = "Test*"`
     - `markers` definitions

2. Create `.coveragerc` with:
   - `[run]` section with:
     - `source = src/flight_delay_explorer`
     - `omit = tests/*`
   - `[report]` section with:
     - `exclude_lines` for pragmas and debug code
     - `fail_under = 90`

3. **Verify test passes**: Run `pytest tests/test_dev_tools.py -v` and confirm success

### Step 6.3: Create Development Tools Implementation Tests
**Goal**: Establish TDD foundation with failing tests that check tool execution

**Tasks**:
1. Create test for actual tool execution in `tests/test_tool_execution.py`:
   - Test running Black formatter on sample code
   - Test running Ruff linter on sample code
   - Test running MyPy type checker on sample code
   - Test running coverage analysis on tests
   - Include assertions to verify tool outputs and exit codes
   - Test error handling for each tool with invalid inputs

2. **Verify test fails**: Run `pytest tests/test_tool_execution.py -v` and confirm failure

### Step 6.4: Implement Development Tools Scripts
**Goal**: Create script commands to execute development tools to make tests pass

**Tasks**:
1. Update `pyproject.toml` with `[tool.poetry.scripts]` or `[project.scripts]`:
   - Add `format = "black src tests"` command
   - Add `lint = "ruff check src tests"` command
   - Add `typecheck = "mypy src tests"` command
   - Add `test = "pytest"` command
   - Add `coverage = "pytest --cov=src/flight_delay_explorer tests/"` command

2. Create pre-commit hooks in `.pre-commit-config.yaml`:
   - Add Black formatting hook
   - Add Ruff linting hook
   - Add MyPy type checking hook
   - Configure hooks to run on staged files

3. **Verify test passes**: Run `pytest tests/test_tool_execution.py -v` and confirm success

## Phase 7: Version Control Setup

### Step 7.1: Create Version Control Tests
**Goal**: Establish TDD foundation with failing tests for version control configuration

**Tasks**:
1. Create test for version control setup in `tests/test_version_control.py`:
   - Test `.gitignore` file existence and content
   - Test Git repository initialization
   - Test basic Git operations (add, commit, status)
   - Test branch creation and switching
   - Include tests for common Git workflows (feature branch, merge)
   - Test ignored files are actually ignored by Git

2. **Verify test fails**: Run `pytest tests/test_version_control.py -v` and confirm failure

### Step 7.2: Implement Version Control Setup
**Goal**: Create proper Git configuration to make tests pass

**Tasks**:
1. Create comprehensive `.gitignore` file:
   - Add Python-specific patterns:
     - `__pycache__/`
     - `*.py[cod]`
     - `*$py.class`
     - `.pytest_cache/`
     - `.coverage`
     - `.coverage.*`
     - `htmlcov/`
   - Add environment-specific patterns:
     - `.env`
     - `.venv/`
     - `env/`
     - `venv/`
     - `ENV/`
   - Add editor-specific patterns:
     - `.idea/`
     - `.vscode/*`
     - `!.vscode/settings.json`
     - `!.vscode/tasks.json`
     - `!.vscode/extensions.json`
   - Add build and distribution patterns:
     - `dist/`
     - `build/`
     - `*.egg-info/`

2. Initialize Git repository (if not already done):
   - Run `git init`
   - Configure user name and email
   - Create initial commit with basic project structure
   - Create development branch as default working branch

3. Create Git hooks in `.git/hooks/`:
   - Add `pre-commit` hook to run code quality tools
   - Add `commit-msg` hook to enforce commit message format
   - Add `pre-push` hook to run full test suite

4. Create `CONTRIBUTING.md` with:
   - Git workflow guidelines
   - Branch naming conventions
   - Commit message format
   - Pull request process
   - Code review checklist

5. **Verify test passes**: Run `pytest tests/test_version_control.py -v` and confirm success

### Step 7.3: Create Git Workflow Tests
**Goal**: Establish TDD foundation with failing tests for Git workflows

**Tasks**:
1. Create test for Git workflows in `tests/test_git_workflows.py`:
   - Test feature branch workflow
   - Test commit message validation
   - Test pre-commit hook execution
   - Test merge conflict resolution
   - Include tests for collaboration scenarios

2. **Verify test fails**: Run `pytest tests/test_git_workflows.py -v` and confirm failure

### Step 7.4: Implement Git Workflow Documentation
**Goal**: Create comprehensive Git workflow guidelines to make tests pass

**Tasks**:
1. Update `CONTRIBUTING.md` with detailed workflow guidelines:
   - Branch strategy (feature branches, release branches, hotfixes)
   - Commit message conventions:
     - Format: `<type>(<scope>): <subject>`
     - Types: feat, fix, docs, style, refactor, test, chore
     - Examples and best practices
   - Pull request process:
     - PR template
     - Review requirements
     - Merge strategies
   - Versioning strategy (semantic versioning)

2. Create PR template in `.github/PULL_REQUEST_TEMPLATE.md`:
   - Description section
   - Related issue section
   - Checklist of requirements
   - Testing instructions

3. **Verify test passes**: Run `pytest tests/test_git_workflows.py -v` and confirm success

## Success Criteria

### Phase 1: Test-Driven CLI Foundation
- [ ] `fetch` command test passes with colored table output
- [ ] CLI displays properly formatted flight delay data with specified colors
- [ ] Test fails first, then passes after implementation

### Phase 2: Core Package Architecture
- [ ] Data models tests pass with proper type safety
- [ ] Configuration management tests pass with environment variable loading
- [ ] All enum values and dataclass properties work as specified
- [ ] `.env.example` file created with required variables

### Phase 3: API Client Setup
- [ ] Logging utility tests pass with proper formatting and output destinations
- [ ] API client tests pass with proper error handling and response parsing
- [ ] Proper handling of API authentication and errors
- [ ] Retry logic works with exponential backoff

### Phase 4: Data Parser
- [ ] Data parser tests pass with proper JSON file parsing and mapping to models
- [ ] Parser correctly classifies flight delays into appropriate categories
- [ ] Error handling properly manages invalid input and missing fields

### Phase 5: CLI Orchestration
- [ ] CLI properly integrates all components (API client, config, parser)
- [ ] Integration tests pass with mocked API responses
- [ ] Error handling works across component boundaries
- [ ] Manual verification with real API succeeds
- [ ] Progress indicators display correctly for long-running operations

### Phase 6: Development Tools Configuration
- [ ] Development tools configuration files exist and contain required settings
- [ ] Black formatting runs successfully on codebase
- [ ] Ruff linter passes with no errors
- [ ] MyPy type checking passes with specified strictness levels
- [ ] Test coverage meets minimum threshold (90%)
- [ ] Pre-commit hooks execute successfully

### Phase 7: Version Control Setup
- [ ] `.gitignore` properly excludes specified files and directories
- [ ] Git repository initialized with proper default branch
- [ ] Git hooks execute successfully (pre-commit, commit-msg)
- [ ] CONTRIBUTING.md contains comprehensive workflow guidelines
- [ ] PR template exists with required sections

### Overall
- [ ] All TDD cycles follow the pattern: write test, verify test fails, implement solution, verify test passes
- [ ] All components work together correctly in end-to-end testing
