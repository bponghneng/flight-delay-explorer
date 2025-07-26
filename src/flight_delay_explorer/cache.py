"""Cache for flight data."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Optional

from .models import DelayCategory, FlightRecord
from .utils.logging import setup_logger

CACHE_DIR = Path(".cache")


def get_cache_key(params: dict[str, Any]) -> str:
    """Generate a cache key from request parameters."""
    # Create a consistent hash from the query parameters
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(params_str.encode()).hexdigest()


def load_from_cache(cache_key: str, logger: Optional[logging.Logger] = None) -> Optional[list[FlightRecord]]:
    """Load flight data from cache if available."""
    logger = logger or setup_logger("cache")
    cache_file = CACHE_DIR / f"{cache_key}.json"

    if cache_file.exists():
        logger.info(f"Loading from cache: {cache_key}")
        try:
            with open(cache_file, "r") as f:
                data = json.load(f)
                return [FlightRecord(**record) for record in data]
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error loading cache file {cache_file}: {e}")
            return None
    return None


class CustomEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, DelayCategory):
            return o.value
        return super().default(o)


def save_to_cache(cache_key: str, data: list[FlightRecord], logger: Optional[logging.Logger] = None):
    """Save flight data to cache."""
    logger = logger or setup_logger("cache")
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{cache_key}.json"

    try:
        with open(cache_file, "w") as f:
            json.dump([record.model_dump() for record in data], f, indent=4, cls=CustomEncoder)
        logger.info(f"Saved to cache: {cache_key}")
    except IOError as e:
        logger.error(f"Error saving to cache file {cache_file}: {e}")
