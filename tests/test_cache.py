"""Tests for the cache module."""

import json
import logging
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from flight_delay_explorer.cache import (
    CACHE_DIR,
    get_cache_key,
    load_from_cache,
    save_to_cache,
)
from flight_delay_explorer.models import DelayCategory, FlightRecord

# Sample flight records for testing
SAMPLE_RECORDS = [
    FlightRecord(
        arrival_delay=30,
        destination_icao="JFK",
        flight_date="2023-01-01",
        flight_icao="AAL123",
        flight_status=DelayCategory.MINOR_DELAY,
        origin_icao="LAX",
    ),
    FlightRecord(
        arrival_delay=0,
        destination_icao="SFO",
        flight_date="2023-01-01",
        flight_icao="UAL456",
        flight_status=DelayCategory.ON_TIME,
        origin_icao="ORD",
    ),
]


@pytest.fixture(autouse=True)
def setup_cache_dir(tmp_path):
    """Ensure the cache directory for tests is managed."""
    original_cache_dir = CACHE_DIR
    # Redirect cache to a temporary directory for tests
    new_cache_dir = tmp_path / ".cache"
    new_cache_dir.mkdir(exist_ok=True)

    with patch("flight_delay_explorer.cache.CACHE_DIR", new_cache_dir):
        yield new_cache_dir

    # Cleanup is handled by pytest's tmp_path fixture


def test_get_cache_key():
    """Test cache key generation."""
    params1 = {"flight_date": "2023-01-01", "param": "value1"}
    params2 = {"flight_date": "2023-01-01", "param": "value2"}
    params3 = {"param": "value1", "flight_date": "2023-01-01"}  # Order shouldn't matter

    key1 = get_cache_key(params1)
    key2 = get_cache_key(params2)
    key3 = get_cache_key(params3)

    assert isinstance(key1, str)
    assert len(key1) == 32  # MD5 hash length
    assert key1 != key2
    assert key1 == key3


def test_save_to_cache(setup_cache_dir):
    """Test saving data to the cache."""
    cache_key = "test_key_save"
    save_to_cache(cache_key, SAMPLE_RECORDS)

    cache_file = setup_cache_dir / f"{cache_key}.json"
    assert cache_file.exists()

    with open(cache_file, "r") as f:
        data = json.load(f)

    assert len(data) == len(SAMPLE_RECORDS)
    assert data[0]["flight_icao"] == "AAL123"


def test_load_from_cache_hit(setup_cache_dir):
    """Test loading data from an existing cache file."""
    cache_key = "test_key_load_hit"
    cache_file = setup_cache_dir / f"{cache_key}.json"

    # Manually create a cache file
    with open(cache_file, "w") as f:
        from flight_delay_explorer.cache import CustomEncoder
        json.dump([record.model_dump() for record in SAMPLE_RECORDS], f, cls=CustomEncoder)

    records = load_from_cache(cache_key)

    assert records is not None
    assert len(records) == len(SAMPLE_RECORDS)
    assert records[0].flight_icao == "AAL123"


def test_load_from_cache_miss():
    """Test loading data when the cache file does not exist."""
    records = load_from_cache("non_existent_key")
    assert records is None


def test_load_from_cache_invalid_json(setup_cache_dir):
    """Test loading data from a corrupt/invalid cache file."""
    cache_key = "test_key_invalid_json"
    cache_file = setup_cache_dir / f"{cache_key}.json"

    # Create a malformed JSON file
    with open(cache_file, "w") as f:
        f.write("{'invalid': 'json',}")

    logger = MagicMock(spec=logging.Logger)
    records = load_from_cache(cache_key, logger=logger)

    assert records is None
    logger.error.assert_called_once()


def test_save_to_cache_io_error():
    """Test handling of IO errors during cache saving."""
    cache_key = "test_key_io_error"
    logger = MagicMock(spec=logging.Logger)

    # Use mock_open to simulate an IOError
    m = mock_open()
    with patch("builtins.open", m):
        m.side_effect = IOError("Disk full")
        save_to_cache(cache_key, SAMPLE_RECORDS, logger=logger)

    logger.error.assert_called_once()
    assert "Error saving to cache file" in logger.error.call_args[0][0]
