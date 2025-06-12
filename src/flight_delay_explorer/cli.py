"""CLI interface for Flight Delay Explorer."""

import datetime
from pathlib import Path
from typing import Optional

import httpx
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .api.client import AviationStackClient
from .config import Settings
from .models import DelayCategory, FlightRecord, QueryParams
from .utils.logging import setup_logger

# Type-annotated Typer app
app: typer.Typer = typer.Typer(
    help="Flight Delay Explorer - Process airline on-time performance data",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command()
def fetch(
    flight_date: str = typer.Option(
        ..., "--flight-date", help="Flight date in YYYY-MM-DD format"
    ),
    save_to_file: Optional[str] = typer.Option(
        None, "--save-to-file", help="Save raw API response to JSON file"
    ),
    log_level: str = typer.Option(
        "INFO", "--log-level", help="Set logging level (DEBUG, INFO, WARNING, ERROR)"
    ),
    show_progress: bool = typer.Option(
        True, "--show-progress/--no-progress", help="Show progress indicators"
    ),
) -> None:
    """Fetch flight delay data for a specific date."""
    # Set up logging
    log_level_map = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}

    logger = setup_logger(
        "flight_delay_cli", level=log_level_map.get(log_level.upper(), 20)
    )

    logger.info(f"Starting flight data fetch for date: {flight_date}")

    # Date validation
    try:
        datetime.datetime.strptime(flight_date, "%Y-%m-%d")
    except ValueError:
        error_msg = "Invalid date format. Please use YYYY-MM-DD format."
        logger.error(error_msg)
        console.print(f"[red]Error:[/red] {error_msg}")
        raise typer.Exit(1) from None

    # Initialize settings
    try:
        settings = Settings()  # Settings loads from environment variables
        logger.debug("Settings loaded successfully")
    except Exception as e:
        error_msg = f"Configuration error: {e}"
        logger.error(error_msg)
        console.print(f"[red]Error:[/red] {error_msg}")
        console.print(
            "[yellow]Hint:[/yellow] Set FLIGHT_ACCESS_KEY environment variable"
        )
        raise typer.Exit(1) from e

    # Initialize API client
    api_client = AviationStackClient(settings, logger)
    query_params = QueryParams(flight_date=flight_date)

    # Fetch data with progress indicator
    flight_records: list[FlightRecord] = []

    try:
        if show_progress:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("Fetching flight data...", total=None)
                flight_records = api_client.get_flights(query_params)
                progress.update(task, description="✓ Flight data fetched successfully")
        else:
            flight_records = api_client.get_flights(query_params)

        logger.info(f"Successfully fetched {len(flight_records)} flight records")

    except httpx.HTTPStatusError as e:
        error_msg = f"API error: HTTP {e.response.status_code}"
        logger.error(f"{error_msg}: {e}")

        if e.response.status_code == 401:
            console.print(f"[red]Error:[/red] {error_msg} - Unauthorized")
            console.print("[yellow]Hint:[/yellow] Check your API access key")
        elif e.response.status_code == 429:
            console.print(f"[red]Error:[/red] {error_msg} - Rate limit exceeded")
            console.print(
                "[yellow]Hint:[/yellow] Try again later or upgrade your API plan"
            )
        else:
            console.print(f"[red]Error:[/red] {error_msg}")

        raise typer.Exit(1) from e

    except httpx.ConnectError as e:
        error_msg = f"Network error: {e}"
        logger.error(error_msg)
        console.print("[red]Error:[/red] Connection failed")
        console.print("[yellow]Hint:[/yellow] Check your internet connection")
        raise typer.Exit(1) from e

    except Exception as e:
        error_msg = f"Unexpected error: {e}"
        logger.error(error_msg)
        console.print(f"[red]Error:[/red] {error_msg}")
        raise typer.Exit(1) from e

    # Save to file if requested
    if save_to_file:
        try:
            # Create a simplified representation for saving
            save_data = {
                "query_date": flight_date,
                "record_count": len(flight_records),
                "flights": [
                    {
                        "flight_icao": record.flight_icao,
                        "origin_icao": record.origin_icao,
                        "destination_icao": record.destination_icao,
                        "arrival_delay": record.arrival_delay,
                        "flight_status": record.flight_status.value,
                        "flight_date": record.flight_date,
                    }
                    for record in flight_records
                ],
            }

            import json

            save_path = Path(save_to_file)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with save_path.open("w") as f:
                json.dump(save_data, f, indent=2)

            logger.info(f"Data saved to {save_to_file}")
            console.print(f"[green]✓[/green] Data saved to {save_to_file}")

        except Exception as e:
            logger.warning(f"Failed to save data to file: {e}")
            console.print(f"[yellow]Warning:[/yellow] Could not save to file: {e}")

    # Display results
    if not flight_records:
        console.print("[yellow]No flight data found for the specified date.[/yellow]")
        logger.info("No flight records returned from API")
        return

    # Create Rich table with colored columns
    table = Table(title=f"Flight Delay Data - {flight_date}")
    table.add_column("Date", style="cyan")
    table.add_column("Flight", style="magenta")
    table.add_column("Route", style="green")
    table.add_column("Delay", style="yellow")
    table.add_column("Status", style="red")

    # Add data rows
    for record in flight_records:
        route = f"{record.origin_icao} → {record.destination_icao}"
        delay_str = f"{record.arrival_delay} min" if record.arrival_delay > 0 else "N/A"

        # Use the enum value for better display
        status_display = record.flight_status.value

        table.add_row(
            record.flight_date, record.flight_icao, route, delay_str, status_display
        )

    console.print(table)

    # Summary statistics
    if len(flight_records) > 1:
        summary_stats = _generate_summary_stats(flight_records)
        console.print("\n[bold]Summary:[/bold]")
        console.print(f"  Total flights: {summary_stats['total']}")
        console.print(f"  On time: {summary_stats['on_time']}")
        console.print(f"  Delayed: {summary_stats['delayed']}")
        console.print(f"  Cancelled: {summary_stats['cancelled']}")
        console.print(f"  Average delay: {summary_stats['avg_delay']:.1f} minutes")

        logger.info(f"Summary: {summary_stats}")


def _generate_summary_stats(records: list[FlightRecord]) -> dict[str, float]:
    """Generate summary statistics for flight records."""
    total = len(records)
    on_time = sum(1 for r in records if r.flight_status == DelayCategory.ON_TIME)
    delayed = sum(
        1
        for r in records
        if r.flight_status
        in [
            DelayCategory.MINOR_DELAY,
            DelayCategory.MAJOR_DELAY,
            DelayCategory.SEVERE_DELAY,
        ]
    )
    cancelled = sum(1 for r in records if r.flight_status == DelayCategory.CANCELLED)

    # Calculate average delay (excluding cancelled flights)
    delay_records = [r for r in records if r.flight_status != DelayCategory.CANCELLED]
    avg_delay = (
        sum(r.arrival_delay for r in delay_records) / len(delay_records)
        if delay_records
        else 0
    )

    return {
        "total": total,
        "on_time": on_time,
        "delayed": delayed,
        "cancelled": cancelled,
        "avg_delay": avg_delay,
    }


if __name__ == "__main__":
    app()
