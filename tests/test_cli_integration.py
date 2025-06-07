"""Comprehensive integration tests for CLI commands."""

import logging
import os
from unittest.mock import Mock, patch

import httpx
import pytest
from typer.testing import CliRunner

from flight_delay_explorer.cli import app
from flight_delay_explorer.config import Settings
from flight_delay_explorer.models import DelayCategory, FlightRecord


@pytest.fixture
def mock_settings():
    """Create mock settings for testing."""
    return Settings(
        access_key="test-api-key",
        base_url="https://api.aviationstack.com/v1",
        max_retries=3,
        timeout_seconds=30,
    )


@pytest.fixture
def sample_api_response():
    """Sample API response data."""
    return {
        "pagination": {"limit": 100, "offset": 0, "count": 3, "total": 3},
        "data": [
            {
                "flight_date": "2024-01-01",
                "flight_status": "landed",
                "departure": {
                    "airport": "John F Kennedy International",
                    "iata": "JFK",
                    "icao": "KJFK",
                    "delay": 15,
                },
                "arrival": {
                    "airport": "Los Angeles International",
                    "iata": "LAX",
                    "icao": "KLAX",
                    "delay": 25,
                },
                "flight": {"iata": "AA123", "icao": "AAL123"},
            },
            {
                "flight_date": "2024-01-01",
                "flight_status": "cancelled",
                "departure": {
                    "airport": "Chicago O'Hare International",
                    "iata": "ORD",
                    "icao": "KORD",
                    "delay": None,
                },
                "arrival": {
                    "airport": "Denver International",
                    "iata": "DEN",
                    "icao": "KDEN",
                    "delay": None,
                },
                "flight": {"iata": "UA456", "icao": "UAL456"},
            },
            {
                "flight_date": "2024-01-01",
                "flight_status": "landed",
                "departure": {
                    "airport": "Miami International",
                    "iata": "MIA",
                    "icao": "KMIA",
                    "delay": 5,
                },
                "arrival": {
                    "airport": "Atlanta Hartsfield-Jackson International",
                    "iata": "ATL",
                    "icao": "KATL",
                    "delay": 120,
                },
                "flight": {"iata": "DL789", "icao": "DAL789"},
            },
        ],
    }


class TestCLIIntegration:
    """Test CLI integration with all components."""

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    @patch("flight_delay_explorer.cli.setup_logger")
    def test_fetch_command_api_integration(
        self,
        mock_setup_logger,
        mock_settings_class,
        mock_client_class,
        sample_api_response,
    ):
        """Test CLI integration with AviationStack API client."""
        runner = CliRunner()

        # Setup mocks
        mock_logger = Mock(spec=logging.Logger)
        mock_setup_logger.return_value = mock_logger

        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create expected FlightRecord objects
        expected_records = [
            FlightRecord(
                arrival_delay=25,
                destination_icao="KLAX",
                flight_date="2024-01-01",
                flight_icao="AAL123",
                flight_status=DelayCategory.MINOR_DELAY,
                origin_icao="KJFK",
            ),
            FlightRecord(
                arrival_delay=0,
                destination_icao="KDEN",
                flight_date="2024-01-01",
                flight_icao="UAL456",
                flight_status=DelayCategory.CANCELLED,
                origin_icao="KORD",
            ),
            FlightRecord(
                arrival_delay=120,
                destination_icao="KATL",
                flight_date="2024-01-01",
                flight_icao="DAL789",
                flight_status=DelayCategory.MAJOR_DELAY,
                origin_icao="KMIA",
            ),
        ]

        mock_client.get_flights.return_value = expected_records

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Verify command executed successfully
        assert result.exit_code == 0

        # Verify API client was properly initialized
        mock_settings_class.assert_called_once()
        mock_client_class.assert_called_once_with(mock_settings, mock_logger)

        # Verify API client was called with correct parameters
        mock_client.get_flights.assert_called_once()
        call_args = mock_client.get_flights.call_args[0][0]
        assert call_args.flight_date == "2024-01-01"

        # Verify output contains flight data
        assert "Flight Delay Data" in result.stdout
        assert "AAL123" in result.stdout
        assert "KJFK → KLAX" in result.stdout
        assert "cancelled" in result.stdout
        assert "major delay" in result.stdout

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_api_authentication_failure(
        self, mock_settings_class, mock_client_class
    ):
        """Test CLI handling of API authentication failures."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock authentication error
        mock_client.get_flights.side_effect = httpx.HTTPStatusError(
            message="Unauthorized", request=Mock(), response=Mock(status_code=401)
        )

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "invalid-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Should fail with authentication error
        assert result.exit_code != 0
        assert (
            "HTTP" in result.stdout
            or "401" in result.stdout
            or "Unauthorized" in result.stdout
        )

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_network_connectivity_issues(
        self, mock_settings_class, mock_client_class
    ):
        """Test CLI handling of network connectivity issues."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock network error
        mock_client.get_flights.side_effect = httpx.ConnectError("Connection failed")

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Should fail with network error
        assert result.exit_code != 0
        assert "Connection" in result.stdout or "network" in result.stdout.lower()

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_rate_limiting_responses(
        self, mock_settings_class, mock_client_class
    ):
        """Test CLI handling of rate limiting responses."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock rate limit error
        mock_client.get_flights.side_effect = httpx.HTTPStatusError(
            message="Rate limit exceeded",
            request=Mock(),
            response=Mock(status_code=429),
        )

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Should fail with rate limit error
        assert result.exit_code != 0
        assert "429" in result.stdout or "rate limit" in result.stdout.lower()

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_malformed_api_responses(
        self, mock_settings_class, mock_client_class
    ):
        """Test CLI handling of malformed API responses."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock malformed response error
        mock_client.get_flights.side_effect = ValueError("Invalid response format")

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Should fail with parsing error
        assert result.exit_code != 0
        assert "Invalid" in result.stdout or "format" in result.stdout.lower()

    @patch("flight_delay_explorer.cli.setup_logger")
    def test_fetch_command_comprehensive_logging(self, mock_setup_logger):
        """Test comprehensive logging throughout the process."""
        runner = CliRunner()

        mock_logger = Mock(spec=logging.Logger)
        mock_setup_logger.return_value = mock_logger

        with (
            patch("flight_delay_explorer.cli.AviationStackClient") as mock_client_class,
            patch("flight_delay_explorer.cli.Settings") as mock_settings_class,
            patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}),
        ):

            mock_settings = Mock()
            mock_settings_class.return_value = mock_settings

            mock_client = Mock()
            mock_client_class.return_value = mock_client
            mock_client.get_flights.return_value = []

            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Verify logging was set up
        mock_setup_logger.assert_called()

        # Verify command executed
        assert result.exit_code == 0

    def test_fetch_command_parameter_validation(self):
        """Test command parameter validation."""
        runner = CliRunner()

        # Test missing required parameter
        result = runner.invoke(app, [])
        assert result.exit_code != 0
        assert "Missing option" in result.stderr or "required" in result.stderr.lower()

        # Test invalid date format
        result = runner.invoke(app, ["--flight-date", "invalid-date"])
        assert result.exit_code != 0
        assert "Invalid date format" in result.stdout

        # Test various invalid date formats
        invalid_dates = ["2024-13-01", "2024-01-32", "not-a-date", ""]
        for invalid_date in invalid_dates:
            result = runner.invoke(app, ["--flight-date", invalid_date])
            assert result.exit_code != 0

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_display_formatting(
        self, mock_settings_class, mock_client_class
    ):
        """Test display of fetched data in formatted table."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create test records with different delay categories
        test_records = [
            FlightRecord(
                arrival_delay=5,
                destination_icao="KLAX",
                flight_date="2024-01-01",
                flight_icao="ON001",
                flight_status=DelayCategory.ON_TIME,
                origin_icao="KJFK",
            ),
            FlightRecord(
                arrival_delay=45,
                destination_icao="KDEN",
                flight_date="2024-01-01",
                flight_icao="MIN001",
                flight_status=DelayCategory.MINOR_DELAY,
                origin_icao="KORD",
            ),
            FlightRecord(
                arrival_delay=150,
                destination_icao="KATL",
                flight_date="2024-01-01",
                flight_icao="MAJ001",
                flight_status=DelayCategory.MAJOR_DELAY,
                origin_icao="KMIA",
            ),
            FlightRecord(
                arrival_delay=300,
                destination_icao="KSEA",
                flight_date="2024-01-01",
                flight_icao="SEV001",
                flight_status=DelayCategory.SEVERE_DELAY,
                origin_icao="KLAX",
            ),
            FlightRecord(
                arrival_delay=0,
                destination_icao="KBOS",
                flight_date="2024-01-01",
                flight_icao="CAN001",
                flight_status=DelayCategory.CANCELLED,
                origin_icao="KJFK",
            ),
            FlightRecord(
                arrival_delay=60,
                destination_icao="KPHX",
                flight_date="2024-01-01",
                flight_icao="DIV001",
                flight_status=DelayCategory.DIVERTED,
                origin_icao="KLAS",
            ),
        ]

        mock_client.get_flights.return_value = test_records

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Verify command executed successfully
        assert result.exit_code == 0

        # Verify table structure
        assert "Flight Delay Data" in result.stdout
        assert "Date" in result.stdout
        assert "Flight" in result.stdout
        assert "Route" in result.stdout
        assert "Delay" in result.stdout
        assert "Status" in result.stdout

        # Verify all delay categories are displayed
        assert "on time" in result.stdout
        assert "minor delay" in result.stdout
        assert "major delay" in result.stdout
        assert "severe delay" in result.stdout
        assert "cancelled" in result.stdout
        assert "diverted" in result.stdout

        # Verify flight codes are displayed
        assert "ON001" in result.stdout
        assert "MIN001" in result.stdout
        assert "MAJ001" in result.stdout
        assert "SEV001" in result.stdout
        assert "CAN001" in result.stdout
        assert "DIV001" in result.stdout

    @patch("flight_delay_explorer.cli.AviationStackClient")
    @patch("flight_delay_explorer.cli.Settings")
    def test_fetch_command_pagination_large_results(
        self, mock_settings_class, mock_client_class
    ):
        """Test display with pagination for large result sets."""
        runner = CliRunner()

        # Setup mocks
        mock_settings = Mock()
        mock_settings_class.return_value = mock_settings

        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Create large set of test records
        large_record_set = []
        for i in range(50):  # Create 50 records
            large_record_set.append(
                FlightRecord(
                    arrival_delay=i * 2,
                    destination_icao=f"K{i:03d}",
                    flight_date="2024-01-01",
                    flight_icao=f"TEST{i:03d}",
                    flight_status=(
                        DelayCategory.ON_TIME
                        if i % 2 == 0
                        else DelayCategory.MINOR_DELAY
                    ),
                    origin_icao="KJFK",
                )
            )

        mock_client.get_flights.return_value = large_record_set

        # Set environment variable for API key
        with patch.dict(os.environ, {"FLIGHT_ACCESS_KEY": "test-key"}):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Verify command executed successfully
        assert result.exit_code == 0

        # Verify table displays properly with many records
        assert "Flight Delay Data" in result.stdout
        assert "TEST001" in result.stdout  # First record
        assert "TEST049" in result.stdout  # Last record

    def test_fetch_command_configuration_missing_api_key(self):
        """Test error handling when API key is missing."""
        runner = CliRunner()

        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(app, ["--flight-date", "2024-01-01"])

        # Should fail due to missing API key
        assert result.exit_code != 0
        assert (
            "required" in result.stdout.lower()
            or "api" in result.stdout.lower()
            or "key" in result.stdout.lower()
        )
