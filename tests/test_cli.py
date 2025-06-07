"""Tests for CLI commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from flight_delay_explorer.cli import app


@pytest.fixture
def sample_flight_data():
    """Load sample flight data for testing."""
    fixtures_path = Path(__file__).parent / "fixtures" / "sample_flight_data.json"
    with fixtures_path.open() as f:
        return json.load(f)


@patch("httpx.Client.get")
def test_fetch_command_displays_colored_table(mock_get, sample_flight_data):
    """Test that fetch command displays flight data in a colored table."""
    runner = CliRunner()

    # Mock HTTP response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_flight_data
    mock_get.return_value = mock_response

    # Set environment variable for API key
    with patch.dict("os.environ", {"FLIGHT_ACCESS_KEY": "test-key"}):
        result = runner.invoke(app, ["--flight-date", "2024-01-01"])

    # Verify command executed successfully
    assert result.exit_code == 0

    # Verify table title is present
    assert "Flight Delay Data" in result.stdout

    # Verify colored column headers are present
    # Note: Rich uses ANSI escape codes for colors
    assert "Date" in result.stdout  # cyan
    assert "Flight" in result.stdout  # magenta
    assert "Route" in result.stdout  # green
    assert "Delay" in result.stdout  # yellow
    assert "Status" in result.stdout  # red

    # Verify sample data appears in output
    assert "AAL123" in result.stdout  # ICAO code
    assert "KJFK" in result.stdout  # ICAO code
    assert "KLAX" in result.stdout  # ICAO code
    assert "cancelled" in result.stdout


def test_fetch_command_with_invalid_date():
    """Test fetch command with invalid date format."""
    runner = CliRunner()

    result = runner.invoke(app, ["--flight-date", "invalid-date"])

    # Should fail with validation error
    assert result.exit_code != 0
    assert "Invalid date format" in result.stdout or "Usage:" in result.stdout
