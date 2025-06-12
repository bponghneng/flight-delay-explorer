# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flight Delay Explorer is a Python CLI tool that processes airline on-time performance CSV data (like DOT/BTS datasets) to generate summary reports including average delays by airline/airport, monthly trends, and delay distribution histograms.

This is an early-stage project focused on learning Python fundamentals, CLI tooling, API integration, and data processing. The current codebase is minimal scaffolding.

## Development Commands

**Package Management**: This project uses `uv` for dependency management.

**Code Quality Tools**:
- `ruff check` - Run linting
- `ruff format` - Format code
- `mypy src/` - Run type checking
- `pytest` - Run test suite
- `pytest --cov=flight_delay_explorer` - Run tests with coverage

**Development Dependencies**: Install with `uv sync --group dev`

## Architecture

**Current Structure**:
- `src/flight_delay_explorer/` - Main package (currently minimal)
- `main.py` - Entry point (placeholder)

**Planned Architecture** (from ROADMAP.md):
- `cli.py` - Typer-based command-line interface
- `api_client.py` - BTS API integration using requests
- `data_parser.py` - pandas-based data processing
- `models.py` - Data structures and classes
- `utils.py` - Helper functions
- `config.py` - Configuration management

**Key Dependencies**:
- `typer` - CLI framework
- `pandas` - Data processing
- `matplotlib` - Data visualization
- `requests` - HTTP client for BTS API

## Data Processing Context

The tool is designed to work with Bureau of Transportation Statistics (BTS) flight delay data. It will:
1. Fetch data via BTS API or process CSV files
2. Transform and clean data using pandas
3. Generate summary statistics and visualizations
4. Export results to CSV format

## Testing Strategy

Uses pytest with coverage reporting. Tests should include:
- Unit tests for individual modules
- Integration tests for API interactions
- Mock objects for external dependencies
- Fixture management for test data

Target >90% code coverage as per project roadmap.
