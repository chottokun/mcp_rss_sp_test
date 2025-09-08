from typing import Optional

from cachetools import TTLCache

from src.models.feed import CacheEntry

# Define a TTL cache with a max size of 1024 entries and a TTL of 300 seconds (5 minutes)
_cache: TTLCache[str, CacheEntry] = TTLCache(maxsize=1024, ttl=300)


class CacheService:
    """
    A simple in-memory cache service for RSS feed entries using a TTL cache.
    """

    def get(self, url: str) -> Optional[CacheEntry]:
        """
        Retrieves a cache entry for a given URL.
        """
        return _cache.get(url)

    def set(self, url:str, entry: CacheEntry):
        """
        Stores a cache entry.
        """
        _cache[url] = entry


# Create a single instance to be used by the application
cache_service = CacheService()
