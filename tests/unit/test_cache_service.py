import pytest
from datetime import datetime, timezone
from pydantic import HttpUrl

from src.services.cache_service import CacheService
from src.models.feed import CacheEntry, FeedItem

@pytest.fixture
def cache_service():
    """
    Provides a clean instance of the CacheService for each test.
    """
    service = CacheService()
    service._cache = {}
    yield service
    service._cache = {}

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

def test_set_and_get_entry(cache_service, sample_cache_entry):
    url = str(sample_cache_entry.feed_url)
    cache_service.set(url, sample_cache_entry)
    retrieved_entry = cache_service.get(url)
    assert retrieved_entry is not None
    assert retrieved_entry == sample_cache_entry

def test_get_nonexistent_entry(cache_service):
    retrieved_entry = cache_service.get("http://nonexistent.com/rss")
    assert retrieved_entry is None
