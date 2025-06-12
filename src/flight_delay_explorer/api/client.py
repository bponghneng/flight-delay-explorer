"""AviationStack API client for Flight Delay Explorer."""

import logging
import time
from typing import Any, Optional, Union

import httpx

from ..config import Settings
from ..models import DelayCategory, FlightRecord, QueryParams
from ..utils.logging import setup_logger


class AviationStackClient:
    """Client for AviationStack API interactions."""

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None):
        """Initialize the API client.

        Args:
            settings: Application settings with API configuration
            logger: Optional logger instance. If None, creates a default logger.
        """
        self._settings = settings
        self._logger = logger or setup_logger(
            "aviation_stack_client", level=logging.INFO
        )

    def get_flights(self, params: QueryParams) -> list[FlightRecord]:
        """Get flight data from AviationStack API.

        Args:
            params: Query parameters for the API request

        Returns:
            List of FlightRecord objects

        Raises:
            httpx.HTTPError: If API request fails after retries
        """
        url = f"{self._settings.base_url}/flights"
        query_params: dict[str, Union[str, int]] = {
            "access_key": self._settings.access_key,
            "flight_date": params.flight_date,
            # Hardcoded to filter flights only to those with arrival delay
            "min_delay_arr": 1,
        }

        self._logger.info(f"Fetching flights for date: {params.flight_date}")
        self._logger.debug(f"API URL: {url}")

        # Retry logic with exponential backoff
        for attempt in range(self._settings.max_retries):
            try:
                with httpx.Client(timeout=self._settings.timeout_seconds) as client:
                    self._logger.debug(f"API request attempt {attempt + 1}")

                    response = client.get(url, params=query_params)

                    if response.status_code == 429:  # Rate limit
                        self._logger.warning(
                            "Rate limit exceeded, retrying with backoff"
                        )
                        if attempt < self._settings.max_retries - 1:
                            backoff_time = 2**attempt  # Exponential backoff
                            time.sleep(backoff_time)
                            continue

                    response.raise_for_status()

                    data = response.json()
                    count = len(data.get("data", []))
                    self._logger.info(f"API request success: {count} records received")
                    self._logger.debug(f"Response status: {response.status_code}")

                    return self._parse_response(data)

            except httpx.HTTPStatusError as e:
                self._logger.error(f"HTTP error on attempt {attempt + 1}: {e}")
                if attempt == self._settings.max_retries - 1:
                    raise
                time.sleep(2**attempt)  # Exponential backoff

            except httpx.ConnectError as e:
                self._logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt == self._settings.max_retries - 1:
                    raise
                time.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                self._logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self._settings.max_retries - 1:
                    raise
                time.sleep(2**attempt)  # Exponential backoff

        # This should never be reached due to the retry logic
        raise RuntimeError("Unexpected end of retry loop")

    def _parse_response(self, data: dict[str, Any]) -> list[FlightRecord]:
        """Parse API response into FlightRecord objects.

        Args:
            data: Raw API response data

        Returns:
            List of FlightRecord objects
        """
        flights = data.get("data", [])
        records = []

        for flight_data in flights:
            try:
                record = self._parse_flight_record(flight_data)
                records.append(record)
            except Exception as e:
                self._logger.warning(f"Failed to parse flight record: {e}")
                continue

        self._logger.debug(f"Successfully parsed {len(records)} flight records")
        return records

    def _parse_flight_record(self, flight_data: dict[str, Any]) -> FlightRecord:
        """Parse individual flight data into FlightRecord.

        Args:
            flight_data: Individual flight data from API

        Returns:
            FlightRecord object
        """
        # Extract flight status and determine delay category
        flight_status = flight_data.get("flight_status", "").lower()
        status_category = self._determine_delay_category(
            flight_status, flight_data.get("arrival", {}).get("delay", 0)
        )

        # Handle arrival delay
        arrival_delay = flight_data.get("arrival", {}).get("delay", 0)
        if arrival_delay is None:
            arrival_delay = 0

        return FlightRecord(
            arrival_delay=arrival_delay,
            destination_icao=flight_data.get("arrival", {}).get("icao", ""),
            flight_date=flight_data.get("flight_date", ""),
            flight_icao=flight_data.get("flight", {}).get("icao", ""),
            flight_status=status_category,
            origin_icao=flight_data.get("departure", {}).get("icao", ""),
        )

    def _determine_delay_category(
        self, flight_status: str, delay_minutes: Optional[int]
    ) -> DelayCategory:
        """Determine the appropriate delay category.

        Args:
            flight_status: Flight status from API
            delay_minutes: Delay in minutes

        Returns:
            DelayCategory enum value
        """
        if flight_status == "cancelled":
            return DelayCategory.CANCELLED
        if flight_status == "diverted":
            return DelayCategory.DIVERTED

        if delay_minutes is None:
            delay_minutes = 0

        if delay_minutes <= 15:
            return DelayCategory.ON_TIME
        if delay_minutes <= 60:
            return DelayCategory.MINOR_DELAY
        if delay_minutes <= 180:
            return DelayCategory.MAJOR_DELAY
        return DelayCategory.SEVERE_DELAY
