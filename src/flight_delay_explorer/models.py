"""Data models for Flight Delay Explorer."""

from dataclasses import dataclass
from enum import Enum


class DelayCategory(Enum):
    """Flight delay categories."""

    CANCELLED = "cancelled"
    DIVERTED = "diverted"
    ON_TIME = "on time"
    MAJOR_DELAY = "major delay"
    MINOR_DELAY = "minor delay"
    SEVERE_DELAY = "severe delay"


@dataclass
class FlightRecord:
    """Represents a single flight record with delay information."""

    arrival_delay: int
    destination_icao: str
    flight_date: str
    flight_icao: str
    flight_status: DelayCategory
    origin_icao: str


@dataclass
class QueryParams:
    """Parameters for querying flight data."""

    flight_date: str
