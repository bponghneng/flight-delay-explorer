"""End-to-end integration tests."""
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
import logging

import pytest
import httpx
from typer.testing import CliRunner

from flight_delay_explorer.cli import app
from flight_delay_explorer.config import Settings
from flight_delay_explorer.models import FlightRecord, DelayCategory, QueryParams
from flight_delay_explorer.api.client import AviationStackClient
from flight_delay_explorer.parsers.data_parser import FlightDataParser
from flight_delay_explorer.utils.logging import setup_logger


@pytest.fixture
def end_to_end_mock_response():
    """Complete mock API response for end-to-end testing."""
    return {
        "pagination": {
            "limit": 100,
            "offset": 0,
            "count": 5,
            "total": 5
        },
        "data": [
            {
                "flight_date": "2024-01-15",
                "flight_status": "landed",
                "departure": {
                    "airport": "John F Kennedy International",
                    "iata": "JFK",
                    "icao": "KJFK",
                    "delay": 10
                },
                "arrival": {
                    "airport": "Los Angeles International",
                    "iata": "LAX",
                    "icao": "KLAX",
                    "delay": 15
                },
                "flight": {
                    "iata": "AA100",
                    "icao": "AAL100"
                }
            },
            {
                "flight_date": "2024-01-15",
                "flight_status": "landed",
                "departure": {
                    "airport": "Chicago O'Hare International",
                    "iata": "ORD",
                    "icao": "KORD",
                    "delay": 5
                },
                "arrival": {
                    "airport": "Denver International",
                    "iata": "DEN",
                    "icao": "KDEN",
                    "delay": 45
                },
                "flight": {
                    "iata": "UA200",
                    "icao": "UAL200"
                }
            },
            {
                "flight_date": "2024-01-15",
                "flight_status": "landed",
                "departure": {
                    "airport": "Miami International",
                    "iata": "MIA",
                    "icao": "KMIA",
                    "delay": 0
                },
                "arrival": {
                    "airport": "Atlanta Hartsfield-Jackson International",
                    "iata": "ATL",
                    "icao": "KATL",
                    "delay": 120
                },
                "flight": {
                    "iata": "DL300",
                    "icao": "DAL300"
                }
            },
            {
                "flight_date": "2024-01-15",
                "flight_status": "cancelled",
                "departure": {
                    "airport": "San Francisco International",
                    "iata": "SFO",
                    "icao": "KSFO",
                    "delay": None
                },
                "arrival": {
                    "airport": "Seattle-Tacoma International",
                    "iata": "SEA",
                    "icao": "KSEA",
                    "delay": None
                },
                "flight": {
                    "iata": "AS400",
                    "icao": "ASA400"
                }
            },
            {
                "flight_date": "2024-01-15",
                "flight_status": "landed",
                "departure": {
                    "airport": "Phoenix Sky Harbor International",
                    "iata": "PHX",
                    "icao": "KPHX",
                    "delay": 30
                },
                "arrival": {
                    "airport": "Las Vegas McCarran International",
                    "iata": "LAS",
                    "icao": "KLAS",
                    "delay": 240
                },
                "flight": {
                    "iata": "WN500",
                    "icao": "SWA500"
                }
            }
        ]
    }


class TestEndToEndIntegration:
    """End-to-end integration tests."""
    
    @patch('httpx.Client.get')
    def test_end_to_end_flow_with_mocked_api(self, mock_get, end_to_end_mock_response):
        """Test complete end-to-end flow with mocked API responses."""
        runner = CliRunner()
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = end_to_end_mock_response
        mock_get.return_value = mock_response
        
        # Set up environment
        with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'test-key-e2e'}):
            result = runner.invoke(app, [
                "--flight-date", "2024-01-15",
                "--log-level", "DEBUG"
            ])
        
        # Verify successful execution
        assert result.exit_code == 0
        
        # Verify output contains expected elements
        assert "Flight Delay Data - 2024-01-15" in result.stdout
        assert "AAL100" in result.stdout
        assert "UAL200" in result.stdout
        assert "DAL300" in result.stdout
        assert "ASA400" in result.stdout
        assert "SWA500" in result.stdout
        
        # Verify delay categories are displayed correctly
        assert "on time" in result.stdout
        assert "minor delay" in result.stdout
        assert "major delay" in result.stdout
        assert "cancelled" in result.stdout
        assert "severe delay" in result.stdout
        
        # Verify summary statistics
        assert "Summary:" in result.stdout
        assert "Total flights: 5" in result.stdout
        assert "On time: 1" in result.stdout
        assert "Delayed: 3" in result.stdout
        assert "Cancelled: 1" in result.stdout
        
        # Verify API was called correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "flights" in call_args[0][0]
        assert call_args[1]["params"]["access_key"] == "test-key-e2e"
        assert call_args[1]["params"]["flight_date"] == "2024-01-15"
    
    @patch('httpx.Client.get')
    def test_end_to_end_with_data_saving(self, mock_get, end_to_end_mock_response):
        """Test end-to-end flow with data saving functionality."""
        runner = CliRunner()
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = end_to_end_mock_response
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_file = Path(temp_dir) / "flight_data.json"
            
            # Set up environment and run command
            with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'test-key-save'}):
                result = runner.invoke(app, [
                    "--flight-date", "2024-01-15",
                    "--save-to-file", str(save_file),
                    "--no-progress"
                ])
            
            # Verify successful execution
            assert result.exit_code == 0
            
            # Verify file was created and contains expected data
            assert save_file.exists()
            
            with open(save_file) as f:
                saved_data = json.load(f)
            
            assert saved_data["query_date"] == "2024-01-15"
            assert saved_data["record_count"] == 5
            assert len(saved_data["flights"]) == 5
            
            # Verify saved flight data structure
            first_flight = saved_data["flights"][0]
            assert first_flight["flight_icao"] == "AAL100"
            assert first_flight["origin_icao"] == "KJFK"
            assert first_flight["destination_icao"] == "KLAX"
            assert first_flight["arrival_delay"] == 15
            assert first_flight["flight_status"] == "on time"
    
    def test_configuration_loading_and_validation(self):
        """Test configuration loading across component boundaries."""
        # Test with valid configuration
        with patch.dict('os.environ', {
            'FLIGHT_ACCESS_KEY': 'test-config-key',
            'FLIGHT_BASE_URL': 'https://custom.api.com/v1',
            'FLIGHT_MAX_RETRIES': '5',
            'FLIGHT_TIMEOUT_SECONDS': '60'
        }):
            settings = Settings()
            
            assert settings.access_key == "test-config-key"
            assert settings.base_url == "https://custom.api.com/v1"
            assert settings.max_retries == 5
            assert settings.timeout_seconds == 60
            
            # Test API client initialization with custom settings
            logger = setup_logger("test-config", level=logging.INFO)
            client = AviationStackClient(settings, logger)
            
            assert client._settings == settings
            assert client._logger == logger
    
    def test_data_parser_integration_with_real_structure(self, end_to_end_mock_response):
        """Test data parser with realistic data structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test_data.json"
            
            # Write mock response to file
            with open(test_file, 'w') as f:
                json.dump(end_to_end_mock_response, f)
            
            # Parse the file
            logger = setup_logger("test-parser", level=logging.INFO)
            parser = FlightDataParser(logger)
            
            records = parser.parse_file(str(test_file))
            
            # Verify parsing results
            assert len(records) == 5
            assert all(isinstance(record, FlightRecord) for record in records)
            
            # Verify delay categorization
            categories = [record.flight_status for record in records]
            assert DelayCategory.ON_TIME in categories
            assert DelayCategory.MINOR_DELAY in categories
            assert DelayCategory.MAJOR_DELAY in categories
            assert DelayCategory.CANCELLED in categories
            assert DelayCategory.SEVERE_DELAY in categories
            
            # Verify specific records
            on_time_record = next(r for r in records if r.flight_status == DelayCategory.ON_TIME)
            assert on_time_record.arrival_delay == 15
            
            cancelled_record = next(r for r in records if r.flight_status == DelayCategory.CANCELLED)
            assert cancelled_record.arrival_delay == 0
            
            severe_delay_record = next(r for r in records if r.flight_status == DelayCategory.SEVERE_DELAY)
            assert severe_delay_record.arrival_delay == 240
    
    def test_logging_integration_across_components(self):
        """Test logging integration across all components."""
        logger = setup_logger("integration-test", level=logging.DEBUG)
        
        # Test logger in different components
        with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'test-logging-key'}):
            settings = Settings()
            client = AviationStackClient(settings, logger)
            parser = FlightDataParser(logger)
            
            # Verify logger integration
            assert client._logger == logger
            assert parser._logger == logger
    
    @patch('httpx.Client.get')
    def test_error_propagation_across_components(self, mock_get):
        """Test that errors propagate correctly across component boundaries."""
        runner = CliRunner()
        
        # Test API error propagation
        mock_get.side_effect = httpx.HTTPStatusError(
            message="Server Error",
            request=Mock(),
            response=Mock(status_code=500)
        )
        
        with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'test-error-key'}):
            result = runner.invoke(app, ["--flight-date", "2024-01-15"])
        
        # Verify error is properly handled at CLI level
        assert result.exit_code != 0
        assert "Error" in result.stdout
    
    @patch('httpx.Client.get')
    def test_command_line_argument_integration(self, mock_get, end_to_end_mock_response):
        """Test various command line arguments and options."""
        runner = CliRunner()
        
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = end_to_end_mock_response
        mock_get.return_value = mock_response
        
        with tempfile.TemporaryDirectory() as temp_dir:
            save_file = Path(temp_dir) / "args_test.json"
            
            # Test with all command line options
            with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'test-args-key'}):
                result = runner.invoke(app, [
                    "--flight-date", "2024-01-15",
                    "--save-to-file", str(save_file),
                    "--log-level", "ERROR",
                    "--no-progress"
                ])
            
            # Verify successful execution
            assert result.exit_code == 0
            
            # Verify file was saved
            assert save_file.exists()
            
            # Verify output (should be less verbose with ERROR log level)
            assert "Flight Delay Data" in result.stdout
    
    def test_data_flow_through_complete_pipeline(self):
        """Test data flowing through the complete processing pipeline."""
        # Create test data that matches API structure
        test_api_data = {
            "data": [
                {
                    "flight_date": "2024-01-15",
                    "flight_status": "landed",
                    "departure": {"icao": "KJFK"},
                    "arrival": {"icao": "KLAX", "delay": 30},
                    "flight": {"icao": "TEST001"}
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test file-based data processing
            test_file = Path(temp_dir) / "pipeline_test.json"
            
            with open(test_file, 'w') as f:
                json.dump(test_api_data, f)
            
            # Parse through data parser
            logger = setup_logger("pipeline-test", level=logging.INFO)
            parser = FlightDataParser(logger)
            
            records = parser.parse_file(str(test_file))
            
            # Verify data transformation
            assert len(records) == 1
            record = records[0]
            
            assert isinstance(record, FlightRecord)
            assert record.flight_icao == "TEST001"
            assert record.origin_icao == "KJFK"
            assert record.destination_icao == "KLAX"
            assert record.arrival_delay == 30
            assert record.flight_status == DelayCategory.MINOR_DELAY
            assert record.flight_date == "2024-01-15"
    
    @patch('httpx.Client.get')
    def test_manual_testing_simulation(self, mock_get, end_to_end_mock_response):
        """Simulate manual testing with realistic API responses."""
        runner = CliRunner()
        
        # Mock HTTP response with realistic data patterns
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = end_to_end_mock_response
        mock_get.return_value = mock_response
        
        # Test different scenarios
        test_scenarios = [
            {
                "date": "2024-01-15",
                "description": "Regular weekday traffic"
            },
            {
                "date": "2024-01-20",
                "description": "Weekend traffic"
            }
        ]
        
        for scenario in test_scenarios:
            with patch.dict('os.environ', {'FLIGHT_ACCESS_KEY': 'manual-test-key'}):
                result = runner.invoke(app, [
                    "--flight-date", scenario["date"],
                    "--log-level", "INFO"
                ])
            
            # Verify each scenario works correctly
            assert result.exit_code == 0
            assert "Flight Delay Data" in result.stdout
            assert scenario["date"] in result.stdout
    
    def test_discrepancy_detection_mock_vs_real_api_behavior(self):
        """Test for potential discrepancies between mock and real API behavior."""
        # Test data structure assumptions
        logger = setup_logger("discrepancy-test", level=logging.INFO)
        
        # Test various edge cases that might differ between mock and real API
        edge_case_data = {
            "data": [
                # Missing optional fields
                {
                    "flight_date": "2024-01-15",
                    "flight_status": "landed",
                    "departure": {"icao": "KJFK"},
                    "arrival": {"icao": "KLAX"},
                    "flight": {"icao": "EDGE001"}
                },
                # Null values
                {
                    "flight_date": "2024-01-15",
                    "flight_status": "cancelled",
                    "departure": {"icao": "KORD"},
                    "arrival": {"icao": "KDEN", "delay": None},
                    "flight": {"icao": "EDGE002"}
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "edge_cases.json"
            
            with open(test_file, 'w') as f:
                json.dump(edge_case_data, f)
            
            # Parse edge cases
            parser = FlightDataParser(logger)
            records = parser.parse_file(str(test_file))
            
            # Verify robust handling
            assert len(records) == 2
            
            # Verify null delay handling
            cancelled_record = next(r for r in records if r.flight_icao == "EDGE002")
            assert cancelled_record.arrival_delay == 0
            assert cancelled_record.flight_status == DelayCategory.CANCELLED