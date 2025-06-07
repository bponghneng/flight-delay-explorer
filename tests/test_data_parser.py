"""Tests for data parser."""

import json
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from flight_delay_explorer.models import DelayCategory, FlightRecord
from flight_delay_explorer.parsers.data_parser import FlightDataParser


@pytest.fixture
def mock_logger():
    """Create mock logger for testing."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def sample_json_data():
    """Sample JSON data matching API structure."""
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
                    "terminal": "4",
                    "gate": "A1",
                    "delay": 15,
                    "scheduled": "2024-01-01T08:00:00+00:00",
                    "estimated": "2024-01-01T08:15:00+00:00",
                    "actual": "2024-01-01T08:20:00+00:00",
                },
                "arrival": {
                    "airport": "Los Angeles International",
                    "iata": "LAX",
                    "icao": "KLAX",
                    "terminal": "6",
                    "gate": "B12",
                    "delay": 25,
                    "scheduled": "2024-01-01T11:00:00+00:00",
                    "estimated": "2024-01-01T11:25:00+00:00",
                    "actual": "2024-01-01T11:30:00+00:00",
                },
                "airline": {"name": "American Airlines", "iata": "AA", "icao": "AAL"},
                "flight": {"number": "123", "iata": "AA123", "icao": "AAL123"},
            },
            {
                "flight_date": "2024-01-01",
                "flight_status": "cancelled",
                "departure": {
                    "airport": "Chicago O'Hare International",
                    "iata": "ORD",
                    "icao": "KORD",
                    "terminal": "1",
                    "gate": None,
                    "delay": None,
                    "scheduled": "2024-01-01T10:00:00+00:00",
                    "estimated": None,
                    "actual": None,
                },
                "arrival": {
                    "airport": "Denver International",
                    "iata": "DEN",
                    "icao": "KDEN",
                    "terminal": "A",
                    "gate": None,
                    "delay": None,
                    "scheduled": "2024-01-01T12:00:00+00:00",
                    "estimated": None,
                    "actual": None,
                },
                "airline": {"name": "United Airlines", "iata": "UA", "icao": "UAL"},
                "flight": {"number": "456", "iata": "UA456", "icao": "UAL456"},
            },
            {
                "flight_date": "2024-01-01",
                "flight_status": "scheduled",
                "departure": {
                    "airport": "Miami International",
                    "iata": "MIA",
                    "icao": "KMIA",
                    "terminal": "D",
                    "gate": "D8",
                    "delay": 5,
                    "scheduled": "2024-01-01T14:00:00+00:00",
                    "estimated": "2024-01-01T14:05:00+00:00",
                    "actual": None,
                },
                "arrival": {
                    "airport": "Atlanta Hartsfield-Jackson International",
                    "iata": "ATL",
                    "icao": "KATL",
                    "terminal": "T",
                    "gate": "T5",
                    "delay": 10,
                    "scheduled": "2024-01-01T16:00:00+00:00",
                    "estimated": "2024-01-01T16:10:00+00:00",
                    "actual": None,
                },
                "airline": {"name": "Delta Air Lines", "iata": "DL", "icao": "DAL"},
                "flight": {"number": "789", "iata": "DL789", "icao": "DAL789"},
            },
        ],
    }


class TestFlightDataParser:
    """Test FlightDataParser class."""

    def test_parser_initialization(self, mock_logger):
        """Test FlightDataParser initialization."""
        parser = FlightDataParser(mock_logger)

        assert parser._logger == mock_logger

    def test_parser_initialization_without_logger(self):
        """Test FlightDataParser initialization without logger."""
        parser = FlightDataParser()

        assert parser._logger is not None  # Should create default logger

    def test_parse_file_successful_parsing(self, mock_logger, sample_json_data):
        """Test successful JSON file parsing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "test_data.json"

            # Write sample data to file
            with json_file.open("w") as f:
                json.dump(sample_json_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            # Verify result
            assert isinstance(result, list)
            assert len(result) == 3
            assert all(isinstance(record, FlightRecord) for record in result)

            # Verify first record (landed flight)
            first_record = result[0]
            assert first_record.flight_icao == "AAL123"
            assert first_record.origin_icao == "KJFK"
            assert first_record.destination_icao == "KLAX"
            assert first_record.arrival_delay == 25
            assert first_record.flight_date == "2024-01-01"
            assert first_record.flight_status == DelayCategory.MINOR_DELAY

            # Verify second record (cancelled flight)
            second_record = result[1]
            assert second_record.flight_status == DelayCategory.CANCELLED
            assert second_record.arrival_delay == 0  # Should default for cancelled

    def test_parse_file_invalid_json(self, mock_logger):
        """Test error handling for invalid JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "invalid.json"

            # Write invalid JSON to file
            with json_file.open("w") as f:
                f.write("{ invalid json content")

            parser = FlightDataParser(mock_logger)

            with pytest.raises(json.JSONDecodeError):
                parser.parse_file(str(json_file))

            # Verify error was logged
            mock_logger.error.assert_called()

    def test_parse_file_missing_file(self, mock_logger):
        """Test error handling for missing files."""
        parser = FlightDataParser(mock_logger)

        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/file.json")

        # Verify error was logged
        mock_logger.error.assert_called()

    def test_parse_file_missing_data_fields(self, mock_logger):
        """Test handling of missing or malformed fields."""
        incomplete_data = {
            "data": [
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    # Missing departure data
                    "arrival": {"icao": "KLAX", "delay": 30},
                    "flight": {"icao": "AAL123"},
                },
                {
                    # Missing flight_date
                    "flight_status": "scheduled",
                    "departure": {"icao": "KJFK"},
                    "arrival": {"icao": "KLAX"},
                    "flight": {"icao": "AAL456"},
                },
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "incomplete.json"

            with json_file.open("w") as f:
                json.dump(incomplete_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            # Should handle missing fields gracefully
            assert isinstance(result, list)
            # Records with missing required fields might be skipped or have defaults
            assert len(result) <= 2

            # Verify warnings were logged for malformed records
            mock_logger.warning.assert_called()

    def test_parse_file_date_format_handling(self, mock_logger):
        """Test proper handling of date formats."""
        date_test_data = {
            "data": [
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    "departure": {"icao": "KJFK"},
                    "arrival": {"icao": "KLAX", "delay": 15},
                    "flight": {"icao": "AAL123"},
                },
                {
                    "flight_date": "2024/01/02",  # Different format
                    "flight_status": "scheduled",
                    "departure": {"icao": "KORD"},
                    "arrival": {"icao": "KDEN", "delay": 5},
                    "flight": {"icao": "UAL456"},
                },
                {
                    "flight_date": "01-03-2024",  # Another format
                    "flight_status": "cancelled",
                    "departure": {"icao": "KMIA"},
                    "arrival": {"icao": "KATL"},
                    "flight": {"icao": "DAL789"},
                },
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "dates.json"

            with json_file.open("w") as f:
                json.dump(date_test_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            # Should handle various date formats
            assert isinstance(result, list)
            assert len(result) >= 1  # At least some records should parse successfully

    def test_parse_file_delay_category_mapping(self, mock_logger):
        """Test mapping of delay information to proper DelayCategory values."""
        delay_test_data = {
            "data": [
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    "departure": {"icao": "KJFK"},
                    "arrival": {"icao": "KLAX", "delay": 5},  # On time
                    "flight": {"icao": "TEST001"},
                },
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    "departure": {"icao": "KORD"},
                    "arrival": {"icao": "KDEN", "delay": 45},  # Minor delay
                    "flight": {"icao": "TEST002"},
                },
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    "departure": {"icao": "KMIA"},
                    "arrival": {"icao": "KATL", "delay": 120},  # Major delay
                    "flight": {"icao": "TEST003"},
                },
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "landed",
                    "departure": {"icao": "KLAX"},
                    "arrival": {"icao": "KJFK", "delay": 240},  # Severe delay
                    "flight": {"icao": "TEST004"},
                },
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "cancelled",
                    "departure": {"icao": "KDEN"},
                    "arrival": {"icao": "KORD"},
                    "flight": {"icao": "TEST005"},
                },
                {
                    "flight_date": "2024-01-01",
                    "flight_status": "diverted",
                    "departure": {"icao": "KATL"},
                    "arrival": {"icao": "KMIA", "delay": 60},
                    "flight": {"icao": "TEST006"},
                },
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "delays.json"

            with json_file.open("w") as f:
                json.dump(delay_test_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            # Verify delay categorization
            assert len(result) == 6

            # Check each delay category
            categories = [record.flight_status for record in result]
            assert DelayCategory.ON_TIME in categories
            assert DelayCategory.MINOR_DELAY in categories
            assert DelayCategory.MAJOR_DELAY in categories
            assert DelayCategory.SEVERE_DELAY in categories
            assert DelayCategory.CANCELLED in categories
            assert DelayCategory.DIVERTED in categories

    def test_parse_file_logging_integration(self, mock_logger, sample_json_data):
        """Test integration with logging utility for debugging and error reporting."""
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "logging_test.json"

            with json_file.open("w") as f:
                json.dump(sample_json_data, f)

            parser = FlightDataParser(mock_logger)
            parser.parse_file(str(json_file))

            # Verify logging calls
            mock_logger.info.assert_called()  # Should log parsing start/completion
            mock_logger.debug.assert_called()  # Should log detailed parsing steps

    def test_parse_file_edge_cases(self, mock_logger):
        """Test edge cases like empty files and invalid data formats."""
        # Test empty file
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_file = Path(temp_dir) / "empty.json"
            empty_file.touch()  # Create empty file

            parser = FlightDataParser(mock_logger)

            with pytest.raises((json.JSONDecodeError, ValueError)):
                parser.parse_file(str(empty_file))

        # Test file with empty data array
        empty_data = {"data": []}
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "empty_data.json"

            with json_file.open("w") as f:
                json.dump(empty_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            assert isinstance(result, list)
            assert len(result) == 0

        # Test file with missing data field
        no_data = {"pagination": {"count": 0}}
        with tempfile.TemporaryDirectory() as temp_dir:
            json_file = Path(temp_dir) / "no_data.json"

            with json_file.open("w") as f:
                json.dump(no_data, f)

            parser = FlightDataParser(mock_logger)
            result = parser.parse_file(str(json_file))

            assert isinstance(result, list)
            assert len(result) == 0
