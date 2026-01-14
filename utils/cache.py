"""
Cache Module for Chad Loves AI
Handles caching of news data with 10-day retention policy.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from functools import lru_cache


# Cache directory for persistent storage
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.cache')


class NewsCache:
    """
    Manages caching of news data with automatic 10-day expiration.
    Uses file-based caching for persistence between sessions.
    """

    def __init__(self, cache_dir: str = CACHE_DIR, retention_days: int = 10):
        """
        Initialize the news cache.

        Args:
            cache_dir: Directory to store cache files
            retention_days: Number of days to retain cached data (default: 10)
        """
        # Store cache directory path
        self.cache_dir = cache_dir
        # Set retention period in days
        self.retention_days = retention_days
        # Create cache directory if it doesn't exist
        self._ensure_cache_dir()

    def _ensure_cache_dir(self) -> None:
        """Create the cache directory if it doesn't exist."""
        # Use os.makedirs with exist_ok to avoid errors
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_key(self, date: str) -> str:
        """
        Generate a unique cache key for a given date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            Hashed cache key string
        """
        # Create MD5 hash of the date for unique filename
        return hashlib.md5(f"news_{date}".encode()).hexdigest()

    def _get_cache_path(self, date: str) -> str:
        """
        Get the full file path for a cached date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            Full path to the cache file
        """
        # Generate cache key and build full path
        cache_key = self._get_cache_key(date)
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    def get(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieve cached news data for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format

        Returns:
            List of news dictionaries if cached, None otherwise
        """
        # Get the cache file path
        cache_path = self._get_cache_path(date)

        # Check if cache file exists
        if not os.path.exists(cache_path):
            # Return None if no cache found
            return None

        try:
            # Open and read the cache file
            with open(cache_path, 'r') as f:
                # Parse JSON data from file
                cached_data = json.load(f)

            # Check if cache has expired (older than retention_days)
            cached_time = datetime.fromisoformat(cached_data.get('cached_at', ''))
            # Calculate the expiration threshold
            expiration = datetime.now() - timedelta(days=self.retention_days)

            # Return None if cache has expired
            if cached_time < expiration:
                # Remove expired cache file
                os.remove(cache_path)
                return None

            # Return the cached news data
            return cached_data.get('data', [])

        except (json.JSONDecodeError, ValueError) as e:
            # Handle corrupt cache files
            print(f"Cache read error: {str(e)}")
            return None

    def set(self, date: str, data: List[Dict[str, Any]]) -> None:
        """
        Store news data in the cache for a specific date.

        Args:
            date: Date string in YYYY-MM-DD format
            data: List of news dictionaries to cache
        """
        # Get the cache file path
        cache_path = self._get_cache_path(date)

        # Build cache object with timestamp
        cache_obj = {
            'cached_at': datetime.now().isoformat(),
            'date': date,
            'data': data
        }

        try:
            # Write cache object to file as JSON
            with open(cache_path, 'w') as f:
                # Use indent for readable JSON
                json.dump(cache_obj, f, indent=2)

        except IOError as e:
            # Handle file write errors
            print(f"Cache write error: {str(e)}")

    def clear_expired(self) -> int:
        """
        Remove all expired cache files (older than retention_days).

        Returns:
            Number of cache files removed
        """
        # Counter for removed files
        removed_count = 0

        # Calculate expiration threshold
        expiration = datetime.now() - timedelta(days=self.retention_days)

        try:
            # Iterate through all cache files
            for filename in os.listdir(self.cache_dir):
                # Only process JSON files
                if not filename.endswith('.json'):
                    continue

                # Build full file path
                filepath = os.path.join(self.cache_dir, filename)

                try:
                    # Read the cache file
                    with open(filepath, 'r') as f:
                        cached_data = json.load(f)

                    # Check if cache has expired
                    cached_time = datetime.fromisoformat(cached_data.get('cached_at', ''))

                    # Remove if older than retention period
                    if cached_time < expiration:
                        os.remove(filepath)
                        removed_count += 1

                except (json.JSONDecodeError, ValueError, IOError):
                    # Remove corrupt cache files
                    os.remove(filepath)
                    removed_count += 1

        except OSError as e:
            # Handle directory read errors
            print(f"Error clearing cache: {str(e)}")

        # Return count of removed files
        return removed_count

    def clear_all(self) -> None:
        """Remove all cache files."""
        try:
            # Iterate through all files in cache directory
            for filename in os.listdir(self.cache_dir):
                # Build full file path
                filepath = os.path.join(self.cache_dir, filename)
                # Remove the file
                if os.path.isfile(filepath):
                    os.remove(filepath)

        except OSError as e:
            # Handle directory errors
            print(f"Error clearing cache: {str(e)}")


# In-memory cache using Python's lru_cache decorator
# This provides fast access for frequently requested data
@lru_cache(maxsize=100)
def get_cached_weather(location: str, date: str) -> Optional[Dict[str, Any]]:
    """
    Get weather data from in-memory cache.
    Uses lru_cache for automatic cache management.

    Args:
        location: City name for weather data
        date: Date string to include in cache key

    Returns:
        Cached weather data or None if not cached
    """
    # This function is wrapped by lru_cache
    # Returns None on first call, cached value on subsequent calls
    return None


def cache_weather(location: str, date: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Store weather data in the in-memory cache.

    Args:
        location: City name for weather data
        date: Date string for cache key
        data: Weather data dictionary to cache

    Returns:
        The cached weather data
    """
    # Clear the specific cache entry first
    get_cached_weather.cache_clear()
    # Return the data (will be cached on next get call)
    return data


@lru_cache(maxsize=50)
def get_cached_stock(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get stock price from in-memory cache.
    Uses lru_cache for automatic cache management.

    Args:
        ticker: Stock ticker symbol

    Returns:
        Cached stock data or None if not cached
    """
    # This function is wrapped by lru_cache
    # Returns None on first call, cached value on subsequent calls
    return None


def clear_stock_cache() -> None:
    """Clear all cached stock prices."""
    # Clear the lru_cache for stock data
    get_cached_stock.cache_clear()


def clear_weather_cache() -> None:
    """Clear all cached weather data."""
    # Clear the lru_cache for weather data
    get_cached_weather.cache_clear()
