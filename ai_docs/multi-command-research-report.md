# Multi-Command Architecture Research Report

## Current Architecture Analysis

Based on examining `src/flight_delay_explorer/cli.py`, the existing architecture uses:

**Current Structure:**
- Single Typer app: `app: typer.Typer = typer.Typer(...)`
- Single command: `@app.command()` decorator on `fetch()` function
- Direct function-based command implementation
- Rich Console integration for output formatting
- Configuration via Settings class and environment variables

**Key Libraries in Use:**
- **typer>=0.16.0** - CLI framework (main command interface)
- **rich>=13.0.0** - Terminal formatting, tables, progress indicators
- **pydantic-settings>=2.0.0** - Configuration management
- **httpx>=0.25.0** - HTTP client for API calls

**Current Command Pattern:**
```python
app: typer.Typer = typer.Typer(help="...", no_args_is_help=True)

@app.command()
def fetch(flight_date: str = typer.Option(...), ...):
    # Single command implementation
```

## Research Findings

### Core Multi-Command Patterns Identified

1. **Multiple Typer App Pattern**: The fundamental approach uses separate `typer.Typer()` instances for each command group, connected via `app.add_typer()`

2. **Modular File Organization**: Best practice is one command group per file with clear separation of concerns

3. **Shared Configuration via Callbacks**: Use `@app.callback()` with `typer.Context` for common options and state management

4. **Rich Integration**: Seamless across command groups using shared console instances and consistent styling

### Conflicting Information Resolved

- **Version Considerations**: Typer 0.16.0+ maintains full backward compatibility with enhanced Click 8.2 support
- **Context Management**: Multiple sources confirm `typer.Context` is the standard approach for shared state
- **Rich Integration**: All sources agree Rich works consistently across command groups when properly imported

## Library Features for Multi-Command Architecture

### **Typer (>=0.16.0)**
- **`typer.Typer()` instances**: Create separate apps for each command group
- **`app.add_typer()`**: Connect command groups to main app with custom names
- **`@app.callback()`**: Define shared configuration and common options
- **`typer.Context`**: Pass shared state between commands via `ctx.obj`
- **One file per command pattern**: Modular organization for command groups
- **Nested subcommands**: Support for hierarchical command structures

**References:**
- [Typer SubCommands](https://typer.tiangolo.com/tutorial/subcommands/)
- [One File Per Command](https://typer.tiangolo.com/tutorial/one-file-per-command/)
- [Using Context](https://typer.tiangolo.com/tutorial/commands/context/)

### **Rich (>=13.0.0)**
- **Shared Console instances**: Consistent styling across command groups via `ctx.obj`
- **Table, Progress, Panel**: UI components that work seamlessly across commands
- **Styling consistency**: Centralized theme management for all command outputs
- **Rich Console injection**: Pass console instance through Typer context

**References:**
- [Rich Documentation](https://rich.readthedocs.io/)
- [Typer + Rich Integration](https://typer.tiangolo.com/tutorial/printing/)

### **Pydantic Settings (>=2.0.0)**
- **Environment-based configuration**: Shared settings across command groups
- **Settings inheritance**: Base configuration classes for common options
- **Validation**: Type-safe configuration management
- **Context integration**: Settings objects passed via Typer context

**References:**
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

## Recommended Architecture Pattern

### Primary Recommendation: Modular Command Group Architecture

```python
# main.py - Entry point
import typer
from rich.console import Console

from .commands import flights, seasonal, degraded

app = typer.Typer()
console = Console()

# Shared configuration via callback
@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    config_file: str = typer.Option("config.json", help="Configuration file path")
):
    """Flight Delay Explorer CLI - Analyze airline performance data."""
    # Store shared configuration
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config_file"] = config_file
    ctx.obj["console"] = console

# Add command groups
app.add_typer(flights.app, name="flights")
app.add_typer(seasonal.app, name="seasonal") 
app.add_typer(degraded.app, name="degraded")

if __name__ == "__main__":
    app()
```

```python
# commands/flights.py - Flight analysis commands
import typer
from rich.table import Table

app = typer.Typer(help="Flight delay analysis commands")

@app.command()
def summary(
    ctx: typer.Context,
    airline: str = typer.Option(None, help="Filter by airline code")
):
    """Generate flight delay summary report."""
    console = ctx.obj["console"]
    verbose = ctx.obj["verbose"]
    
    if verbose:
        console.print("[bold blue]Generating flight summary...[/bold blue]")
    
    # Implementation here
    table = Table(title="Flight Delay Summary")
    # ... table setup and data
    console.print(table)
```

### Recommended Directory Structure
```
main.py                 # Main app with callback for shared config
commands/
  ├── flights.py       # Flight analysis command group
  ├── seasonal.py      # Seasonal analysis command group
  └── degraded.py      # Degradation detection command group
```

### Alternative Approaches

1. **Single File with Groups**: For smaller applications, use the single-file pattern with multiple Typer apps
2. **Nested Commands**: For complex hierarchies, leverage the nested subcommand pattern
3. **Plugin Architecture**: For extensible systems, use dynamic command loading

### Risk Considerations

- **Complexity Growth**: Monitor command hierarchy depth to maintain usability
- **Shared State Management**: Be careful with mutable state in `ctx.obj`
- **Import Dependencies**: Ensure proper module organization to avoid circular imports

### Implementation Guidance

1. Start with command groups (`flights`, `seasonal`, `degraded`)
2. Implement shared configuration through main callback
3. Use Rich consistently across all command groups
4. Leverage type hints for better validation and documentation
5. Consider auto-completion setup for enhanced UX

## Sources & References

- [Typer SubCommands Documentation](https://typer.tiangolo.com/tutorial/subcommands/): Official patterns for command groups
- [One File Per Command](https://typer.tiangolo.com/tutorial/one-file-per-command/): Modular organization approach
- [Nested SubCommands](https://typer.tiangolo.com/tutorial/subcommands/nested-subcommands/): Advanced hierarchical patterns
- [Typer Callbacks](https://typer.tiangolo.com/tutorial/commands/callback/): Shared configuration management
- [Using Context](https://typer.tiangolo.com/tutorial/commands/context/): State management across commands
- [Jacob Kaplan-Moss: Common Arguments](https://jacobian.org/til/common-arguments-with-typer/): Practical shared options pattern
- [CodeCentric: Modern CMD Tools](https://www.codecentric.de/en/knowledge-hub/blog/lets-build-a-modern-cmd-tool-with-python-using-typer-and-rich): Rich integration patterns
- [Typer Release Notes](https://typer.tiangolo.com/release-notes/): Version 0.16.0+ features

## Additional Resources

- Typer Auto-completion documentation for enhanced UX
- Rich styling guides for consistent terminal UI
- Click Context documentation for advanced state management
- FastAPI documentation (same author) for pattern inspiration