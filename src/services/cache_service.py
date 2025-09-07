from typing import Dict, Optional

from src.models.feed import CacheEntry


class CacheService:
    """
    A simple in-memory cache service for RSS feed entries.
    """
    _cache: Dict[str, CacheEntry] = {}

    def get(self, url: str) -> Optional[CacheEntry]:
        """
        Retrieves a cache entry for a given URL.
        """
        return self._cache.get(url)

    def set(self, url: str, entry: CacheEntry):
        """
        Stores a cache entry.
        """
        self._cache[url] = entry

# Create a single instance to be used by the application
cache_service = CacheService()
