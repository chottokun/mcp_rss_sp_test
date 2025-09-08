import time
from datetime import datetime, timezone
from pydantic import HttpUrl
import pytest
from cachetools import TTLCache

# Import the underlying cache object and the service instance to test it
from src.services.cache_service import _cache, cache_service, CacheService
from src.models.feed import CacheEntry, FeedItem

@pytest.fixture(autouse=True)
def clear_cache_before_each_test():
    """
    Fixture to clear the global cache before each test runs.
    This ensures test isolation.
    """
    _cache.clear()
    yield
    _cache.clear()

@pytest.fixture
def sample_cache_entry():
    """Provides a sample CacheEntry for testing."""
    return CacheEntry(
        feed_url=HttpUrl("http://example.com/rss"),
        item=FeedItem(
            title="Test Title",
            link=HttpUrl("http://example.com/item1"),
            published_date=datetime.now(timezone.utc),
            description="Test Description"
        ),
        last_fetched=datetime.now(timezone.utc),
        etag="test-etag"
    )

def test_set_and_get_entry(sample_cache_entry):
    """
    Tests that an entry can be set and then retrieved.
    """
    url = str(sample_cache_entry.feed_url)
    cache_service.set(url, sample_cache_entry)
    retrieved_entry = cache_service.get(url)
    assert retrieved_entry is not None
    assert retrieved_entry == sample_cache_entry

def test_get_nonexistent_entry():
    """
    Tests that getting a nonexistent entry returns None.
    """
    retrieved_entry = cache_service.get("http://nonexistent.com/rss")
    assert retrieved_entry is None

def test_cache_entry_expires_after_ttl(mocker, sample_cache_entry):
    """
    Tests that a cache entry is automatically evicted after its TTL expires.
    """
    # Create a new cache with a very short TTL for this test
    short_ttl_cache = TTLCache(maxsize=10, ttl=0.1)
    mocker.patch('src.services.cache_service._cache', short_ttl_cache)

    url = str(sample_cache_entry.feed_url)

    # Set an entry and verify it's there
    cache_service.set(url, sample_cache_entry)
    assert cache_service.get(url) is not None

    # Wait for longer than the TTL
    time.sleep(0.2)

    # Verify the entry has been evicted
    assert cache_service.get(url) is None
