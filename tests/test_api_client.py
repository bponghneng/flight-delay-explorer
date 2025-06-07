"""Tests for API client."""

import logging
from unittest.mock import Mock, patch

import httpx
import pytest

from flight_delay_explorer.api.client import AviationStackClient
from flight_delay_explorer.config import Settings
from flight_delay_explorer.models import DelayCategory, FlightRecord, QueryParams


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
def mock_logger():
    """Create mock logger for testing."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def sample_api_response():
    """Sample API response data."""
    return {
        "pagination": {"limit": 100, "offset": 0, "count": 2, "total": 2},
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
        ],
    }


class TestAviationStackClient:
    """Test AviationStackClient class."""

    def test_client_initialization(self, mock_settings, mock_logger):
        """Test AviationStackClient initialization."""
        client = AviationStackClient(mock_settings, mock_logger)

        assert client._settings == mock_settings
        assert client._logger == mock_logger

    def test_client_initialization_without_logger(self, mock_settings):
        """Test AviationStackClient initialization without logger."""
        client = AviationStackClient(mock_settings)

        assert client._settings == mock_settings
        assert client._logger is not None  # Should create default logger

    @patch("httpx.Client.get")
    def test_get_flights_successful_request(
        self, mock_get, mock_settings, mock_logger, sample_api_response
    ):
        """Test successful API request to get flights."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        result = client.get_flights(params)

        # Verify API was called with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert "flights" in call_args[0][0]  # URL should contain 'flights' endpoint
        assert call_args[1]["params"]["access_key"] == "test-api-key"
        assert call_args[1]["params"]["flight_date"] == "2024-01-01"

        # Verify result is list of FlightRecord objects
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(record, FlightRecord) for record in result)

        # Verify first record
        first_record = result[0]
        assert first_record.flight_icao == "AAL123"
        assert first_record.origin_icao == "KJFK"
        assert first_record.destination_icao == "KLAX"
        assert first_record.arrival_delay == 25
        assert first_record.flight_status == DelayCategory.MINOR_DELAY

    @patch("httpx.Client.get")
    def test_get_flights_http_error_handling(
        self, mock_get, mock_settings, mock_logger
    ):
        """Test HTTP error handling."""
        # Mock HTTP error response
        mock_get.side_effect = httpx.HTTPStatusError(
            message="Not Found", request=Mock(), response=Mock(status_code=404)
        )

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        with pytest.raises(httpx.HTTPStatusError):
            client.get_flights(params)

        # Verify logging was called
        mock_logger.error.assert_called()

    @patch("httpx.Client.get")
    def test_get_flights_network_error_handling(
        self, mock_get, mock_settings, mock_logger
    ):
        """Test network error handling."""
        # Mock network error
        mock_get.side_effect = httpx.ConnectError("Connection failed")

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        with pytest.raises(httpx.ConnectError):
            client.get_flights(params)

        # Verify logging was called
        mock_logger.error.assert_called()

    @patch("httpx.Client.get")
    def test_get_flights_retry_logic(self, mock_get, mock_settings, mock_logger):
        """Test retry logic for transient failures."""
        # Mock first two calls fail, third succeeds
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        mock_get.side_effect = [
            httpx.ConnectError("Temporary failure"),
            httpx.ConnectError("Temporary failure"),
            mock_response,
        ]

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        result = client.get_flights(params)

        # Should have retried 3 times total
        assert mock_get.call_count == 3
        assert isinstance(result, list)

    @patch("httpx.Client.get")
    def test_get_flights_max_retries_exceeded(
        self, mock_get, mock_settings, mock_logger
    ):
        """Test behavior when max retries are exceeded."""
        # Mock all calls fail
        mock_get.side_effect = httpx.ConnectError("Persistent failure")

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        with pytest.raises(httpx.ConnectError):
            client.get_flights(params)

        # Should have tried max_retries times
        assert mock_get.call_count == mock_settings.max_retries

    @patch("httpx.Client.get")
    def test_get_flights_authentication_header(
        self, mock_get, mock_settings, mock_logger
    ):
        """Test that authentication is properly included in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        client.get_flights(params)

        # Verify access_key is included in request parameters
        call_args = mock_get.call_args
        assert call_args[1]["params"]["access_key"] == "test-api-key"

    @patch("httpx.Client.get")
    def test_get_flights_url_construction(self, mock_get, mock_settings, mock_logger):
        """Test proper URL construction with query parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}
        mock_get.return_value = mock_response

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        client.get_flights(params)

        # Verify URL construction
        call_args = mock_get.call_args
        url = call_args[0][0]
        assert url == f"{mock_settings.base_url}/flights"

    @patch("httpx.Client.get")
    def test_get_flights_response_parsing(
        self, mock_get, mock_settings, mock_logger, sample_api_response
    ):
        """Test response parsing and data extraction."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        result = client.get_flights(params)

        # Verify parsing
        assert len(result) == 2

        # Check cancelled flight is properly categorized
        cancelled_flight = result[1]
        assert cancelled_flight.flight_status == DelayCategory.CANCELLED
        assert cancelled_flight.arrival_delay == 0  # Should default for cancelled

    @patch("httpx.Client.get")
    def test_get_flights_rate_limit_handling(
        self, mock_get, mock_settings, mock_logger
    ):
        """Test rate limit handling and backoff strategies."""
        # Mock rate limit response followed by success
        rate_limit_response = Mock()
        rate_limit_response.status_code = 429
        rate_limit_response.json.return_value = {"error": "Rate limit exceeded"}

        success_response = Mock()
        success_response.status_code = 200
        success_response.json.return_value = {"data": []}

        mock_get.side_effect = [rate_limit_response, success_response]

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        # Should handle rate limit and eventually succeed
        result = client.get_flights(params)

        assert mock_get.call_count == 2
        assert isinstance(result, list)

    @patch("httpx.Client.get")
    def test_get_flights_request_response_logging(
        self, mock_get, mock_settings, mock_logger, sample_api_response
    ):
        """Test request/response logging."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_get.return_value = mock_response

        client = AviationStackClient(mock_settings, mock_logger)
        params = QueryParams(flight_date="2024-01-01")

        client.get_flights(params)

        # Verify logging was called for request/response
        assert mock_logger.info.called
        assert mock_logger.debug.called
