"""Data parser for Flight Delay Explorer."""
import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..models import FlightRecord, DelayCategory
from ..utils.logging import setup_logger


class FlightDataParser:
    """Parser for flight data JSON files."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize the data parser.
        
        Args:
            logger: Optional logger instance. If None, creates a default logger.
        """
        self._logger = logger or setup_logger(
            "flight_data_parser", 
            level=logging.INFO
        )
    
    def parse_file(self, file_path: str) -> List[FlightRecord]:
        """Parse JSON file and convert to FlightRecord objects.
        
        Args:
            file_path: Path to the JSON file to parse
            
        Returns:
            List of FlightRecord objects
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
        """
        file_path_obj = Path(file_path)
        
        self._logger.info(f"Starting to parse file: {file_path}")
        
        if not file_path_obj.exists():
            error_msg = f"File not found: {file_path}"
            self._logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        try:
            with open(file_path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._logger.debug(f"Successfully loaded JSON from {file_path}")
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in file {file_path}: {e}"
            self._logger.error(error_msg)
            raise
        
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {e}"
            self._logger.error(error_msg)
            raise
        
        # Parse the JSON data
        records = self._parse_json_data(data)
        
        self._logger.info(f"Successfully parsed {len(records)} flight records from {file_path}")
        return records
    
    def _parse_json_data(self, data: Dict[str, Any]) -> List[FlightRecord]:
        """Parse JSON data structure into FlightRecord objects.
        
        Args:
            data: Raw JSON data
            
        Returns:
            List of FlightRecord objects
        """
        # Handle missing or empty data field
        flights_data = data.get('data', [])
        
        if not flights_data:
            self._logger.warning("No flight data found in JSON")
            return []
        
        records = []
        for i, flight_data in enumerate(flights_data):
            try:
                record = self._parse_flight_data(flight_data)
                records.append(record)
                self._logger.debug(f"Successfully parsed flight record {i + 1}")
                
            except Exception as e:
                self._logger.warning(f"Failed to parse flight record {i + 1}: {e}")
                continue
        
        self._logger.debug(f"Parsed {len(records)} valid records out of {len(flights_data)} total")
        return records
    
    def _parse_flight_data(self, flight_data: Dict[str, Any]) -> FlightRecord:
        """Parse individual flight data into FlightRecord.
        
        Args:
            flight_data: Individual flight data from JSON
            
        Returns:
            FlightRecord object
            
        Raises:
            ValueError: If required fields are missing
        """
        # Extract required fields with validation
        flight_date = flight_data.get('flight_date')
        if not flight_date:
            raise ValueError("Missing required field: flight_date")
        
        # Normalize date format if needed
        flight_date = self._normalize_date_format(flight_date)
        
        # Extract flight information
        flight_info = flight_data.get('flight', {})
        flight_icao = flight_info.get('icao', '')
        if not flight_icao:
            raise ValueError("Missing required field: flight.icao")
        
        # Extract departure information
        departure_info = flight_data.get('departure', {})
        origin_icao = departure_info.get('icao', '')
        if not origin_icao:
            raise ValueError("Missing required field: departure.icao")
        
        # Extract arrival information
        arrival_info = flight_data.get('arrival', {})
        destination_icao = arrival_info.get('icao', '')
        if not destination_icao:
            raise ValueError("Missing required field: arrival.icao")
        
        # Extract delay information
        arrival_delay = arrival_info.get('delay')
        if arrival_delay is None:
            arrival_delay = 0
        
        # Extract flight status and determine delay category
        flight_status = flight_data.get('flight_status', '').lower()
        status_category = self._determine_delay_category(flight_status, arrival_delay)
        
        # Handle special cases for cancelled/diverted flights
        if status_category in [DelayCategory.CANCELLED, DelayCategory.DIVERTED]:
            arrival_delay = 0  # Reset delay for cancelled/diverted flights
        
        return FlightRecord(
            arrival_delay=arrival_delay,
            destination_icao=destination_icao,
            flight_date=flight_date,
            flight_icao=flight_icao,
            flight_status=status_category,
            origin_icao=origin_icao
        )
    
    def _normalize_date_format(self, date_str: str) -> str:
        """Normalize various date formats to YYYY-MM-DD.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Normalized date string in YYYY-MM-DD format
        """
        # Handle common date formats
        date_str = date_str.strip()
        
        # If already in YYYY-MM-DD format, return as-is
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            return date_str
        
        # Handle YYYY/MM/DD format
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                if len(parts[0]) == 4:  # YYYY/MM/DD
                    return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
                elif len(parts[2]) == 4:  # MM/DD/YYYY
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        
        # Handle MM-DD-YYYY or DD-MM-YYYY format
        if '-' in date_str:
            parts = date_str.split('-')
            if len(parts) == 3:
                if len(parts[2]) == 4:  # MM-DD-YYYY or DD-MM-YYYY
                    # Assume MM-DD-YYYY for now (could be enhanced with locale detection)
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        
        # If we can't parse it, return as-is and let validation handle it
        self._logger.warning(f"Could not normalize date format: {date_str}")
        return date_str
    
    def _determine_delay_category(self, flight_status: str, delay_minutes: int) -> DelayCategory:
        """Determine the appropriate delay category.
        
        Args:
            flight_status: Flight status from JSON
            delay_minutes: Delay in minutes
            
        Returns:
            DelayCategory enum value
        """
        # Handle special statuses first
        if flight_status == 'cancelled':
            return DelayCategory.CANCELLED
        elif flight_status == 'diverted':
            return DelayCategory.DIVERTED
        
        # Categorize by delay duration
        if delay_minutes <= 15:
            return DelayCategory.ON_TIME
        elif delay_minutes <= 60:
            return DelayCategory.MINOR_DELAY
        elif delay_minutes <= 180:
            return DelayCategory.MAJOR_DELAY
        else:
            return DelayCategory.SEVERE_DELAY