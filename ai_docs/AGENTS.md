# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flight Delay Explorer is a Python CLI tool that processes airline on-time performance CSV data (like DOT/BTS datasets) to generate summary reports including average delays by airline/airport, monthly trends, and delay distribution histograms.

This is an early-stage project focused on learning Python fundamentals, CLI tooling, API integration, and data processing. The current codebase is minimal scaffolding.

## Archon Integration & Workflow

**CRITICAL: This project uses Archon for knowledge management, task tracking, and project organization.**

### Core Archon Workflow Principles

#### The Golden Rule: Task-Driven Development with Archon

**MANDATORY: Always complete the full Archon task cycle before any coding:**

1. **Check Current Task** → Review task details and requirements
2. **Research for Task** → Search relevant documentation and examples
3. **Implement the Task** → Write code based on research
4. **Update Task Status** → Move task from "todo" → "doing" → "review"
5. **Get Next Task** → Check for next priority task
6. **Repeat Cycle**

**Task Management Rules:**

- Update all actions to Archon
- Move tasks from "todo" → "doing" → "review" (not directly to complete)
- Maintain task descriptions and add implementation notes
- DO NOT MAKE ASSUMPTIONS - check project documentation for questions

## Workflow Style & Collaboration Rules

### Code Changes & Investigation Workflow

- **Research First**: Investigate thoroughly before proposing solutions. Use search
  tools and documentation to gather facts rather than making assumptions.
- **Discuss Before Implementing**: Present findings and proposed approaches for
  approval before making code changes. Explain options and trade-offs.
- **Respect Original Code**: Try to understand where code came from and what problem
  it's solving before assuming it can be changed.
- **Question Assumptions**: If something doesn't work as expected, investigate the
  root cause. Look for version differences, environment issues, or missing context.

### Problem-Solving Workflow

1. **Analyze**: Read errors carefully and identify the real issue
2. **Research**: Use tools and documentation to understand the problem context
3. **Propose**: Present findings and suggest solution options with pros/cons
4. **Implement**: Only after approval, make minimal necessary changes
5. **Clean Up**: Remove temporary test files or debugging code

### Communication

- Ask clarifying questions when requirements are unclear
- Explain the "why" behind recommendations
- If blocked or uncertain, ask for guidance rather than guessing

## Simplicity-First Mindset

Your guidance is directed by these core principles:

1. **Start with MVP**: Focus on core functionality that delivers immediate value
2. **Avoid Premature Optimization**: Don't add features "just in case"
3. **Minimal Dependencies**: Only add what's absolutely necessary for requirements
4. **Clear Over Clever**: Simple, maintainable solutions over complex architectures

Apply these principles when evaluating whether complex patterns, or advanced optimizations are truly needed or if simpler solutions would suffice.

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
