# Flight Delay Explorer
A command-line tool that ingests airline on-time performance CSVs like the Bureau of Transportation Statistics (DOT) “On-Time Performance” dataset. It processes them and outputs summary reports, like average delays by airline or airport, monthly trends and histograms of delay distributions.

## Background

I started this as part of a series of personal projects to retool my software engineering skills for the agentic engineering age. Here's the prompt I fed into ChatGPT to get started:

> I'm a staff engineer who works at a scaling fintech company. I want to advance my professional skills in some specific areas with a personal programming project. Three skills areas are important for me to learn:
>
> - Python
> - CQRS and event sourcing
> - AI engineering
>
> Can you recommend simple projects I can build as a way to develop skills in these areas?

I got back a list of projects, with three focusing on one of the skills I was interested in and a final one that integrated all three. All of them were perfectly reasonable and well matched to my intention. But they were also perfectly predictable: an expense tracker, a bank microservice, a chatbot for a document collection. So I prompted for something more interesting.

> I like your idea of building one project for each area and then building one that integrates the three. As for a category of application, can you recommend similar projects but in the area of commercial aviation? One idea is using historic airport and airline arrival and departure data to build a point-to-point routing application.

ChatGPT came back with a similar list of projects that was just what I was looking for:

1. Python: Flight Delay Explorer CLI
2. CQRS & Event Sourcing: Flight Status Service
3. AI Engineering: Flight Route Recommendation Chatbot
4. Capstone: Intelligent Flight Planner

## Running Flight Delay Explorer

To run the Flight Delay Explorer locally, follow these steps:

1. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

2. **Set up your AviationStack access key**:
   Copy the `.env.example` file to `.env` and add your AviationStack API key:
   ```
   AVIATIONSTACK_ACCESS_KEY=your_access_key_here
   ```

   You can obtain an API key by signing up at [AviationStack](https://aviationstack.com/).

3. **Run the application**:
   Use the following command to run the Flight Delay Explorer:
   ```bash
   uv run main.py --flight-date 2025-06-01
   ```

   Replace `2025-06-01` with your desired flight date in YYYY-MM-DD format.

   **Note:** Using the free plan, the AviationStack API returns `403` errors for any `--flight-date` that is not today.

### Example Output

```text
                Flight Delay Data - 2025-06-01
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━┓
┃ Date       ┃ Flight  ┃ Route       ┃ Delay   ┃ Status      ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━┩
│ 2025-06-01 │ CES1963 │ ZHHH → ZWYN │ 1 min   │ on time     │
│ 2025-06-01 │         │ KLAL → KLIT │ 38 min  │ minor delay │
│ 2025-06-01 │ JAG6561 │ KMSO → KDFW │ 26 min  │ minor delay │
│ 2025-06-01 │ VLG5540 │ LEMD → LFBO │ 44 min  │ minor delay │
│ 2025-06-01 │ CXA5326 │ ZSNJ → ZUTF │ 25 min  │ minor delay │
│ 2025-06-01 │ APJ773  │ RJBB → WSSS │ N/A     │ on time     │
│ 2025-06-01 │ VJT735  │ RJBB → KDFW │ 1 min   │ on time     │
│ 2025-06-01 │ BAW4002 │ EGLL → EGAE │ N/A     │ on time     │
│ 2025-06-01 │ NJE     │ EDGS → EDDM │ 44 min  │ minor delay │
│ 2025-06-01 │ PIA727  │ OPPS → OERK │ N/A     │ on time     │
└────────────┴─────────┴─────────────┴─────────┴─────────────┘
```

**Note:** Flights with delays of 1-15 minutes are considered "on time" in the above output.

### Command Line Options

- `--flight-date`: (Required) The date for which to fetch flight data in YYYY-MM-DD format
- `--help`: Show help message and exit

## Development

### Setup Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/flight-delay-explorer.git
   cd flight-delay-explorer
   ```

2. **Install dependencies**:
   ```bash
   uv sync --group dev
   ```

3. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

### Git Hooks

This project uses custom Git hooks located in the `.githooks/` directory:

- **pre-commit**: Runs code quality checks including Ruff linting/formatting, MyPy type checking, and file integrity checks
- **pre-push**: Installs the package in development mode and runs the full test suite with coverage checks

The hooks help maintain code quality by automatically checking your code before commits and pushes.

### Testing

Run the test suite with:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src/flight_delay_explorer tests/
```

For more detailed information about contributing to this project, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Work-in-Progress

### June 12, 2025

Today I focused on refining the development toolchain and optimizing the testing infrastructure. The main achievement was consolidating code quality tools by dropping Black and isort in favor of extending Ruff to handle all formatting and linting tasks. This simplification reduces tool complexity while maintaining the same quality standards.

MyPy configuration was significantly enhanced by enabling strict mode for source files, which required careful refinement of type annotations throughout the codebase. While the main application code now passes strict type checking, the test suite still requires adjustments to meet these stricter standards.

I also addressed dot-env handling across the entire application, ensuring consistent environment variable management in both the main code and test suite. Performance optimization of the test suite was another focus area, making the TDD workflow more responsive.

The Git workflow received attention with optimizations to the pre-commit and pre-push hooks, along with corresponding test updates to verify their functionality. I also updated documentation in README.md and CONTRIBUTING.md to reflect these tooling changes.

One key insight from this work was recognizing that agent-generated tests tend to be overengineered. Based on experience from another project, I've learned that better results come from building test plans step-by-step with explicit specifications and human-in-the-loop verification before implementing the actual tests.

The project is now effectively complete and functional once properly configured via .env. The test suite is fast and well-suited for TDD, and the Git workflow checks are both thorough and performant.

### June 7, 2025

This was an exciting milestone day where I executed the complete specification in a single shot to build the entire application. The comprehensive spec I had developed over the previous days was put to the test, and the results were remarkably successful.

I implemented the full application architecture as specified, including the CLI interface, API client, data models, configuration management, and testing infrastructure. The scope covered everything from the Typer-based command-line interface to the AviationStack API integration, data parsing, and rich console output formatting.

The most rewarding aspect was seeing the detailed specification execute flawlessly in one attempt. This validated my approach to specification-driven development and gave me confidence in the prompting methodology I had developed. The application ran successfully with only minor edits required, which was a significant confidence-builder for this approach to AI-assisted development.

However, this experience also taught me that even the most detailed specifications will likely miss some edge cases and implementation details that require human adjustment. While the core functionality worked immediately, I recognized the need for a more thorough refactoring of tests and workflow processes, which I planned to address in the following days.

This successful one-shot implementation represents a major validation of the specification-first approach to building software with AI assistance, while also highlighting the continued importance of human oversight and refinement in the development process.

### June 6, 2025

Today I focused on collaborating with Claude to build a detailed implementation plan for the first milestone of the project. This represents my first experience co-creating a specification document with an AI assistant rather than writing it entirely by hand.

I encountered some interesting challenges with prompt engineering. Initially, Claude would generate code for the entire project at once, which wasn't my intention. I wanted to approach this methodically using Test-Driven Development (TDD) to learn Python programming properly and keep each increment as lean as possible. This required more specific prompting to limit the scope and emphasize the TDD approach in the `specs/core-package-structure.md` file.

The implementation plan now details a phased approach with clear steps:
1. Test-Driven CLI Foundation
2. Core Package Architecture
3. API Client Setup
4. Data Parser Implementation

Each phase follows the strict TDD cycle: write test, verify test fails, implement solution, verify test passes.

Next steps include executing the spec, fixing any issues that arise and getting the generated code into a clean state before moving on to build the specification for the next milestone.
