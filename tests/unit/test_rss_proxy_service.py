import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone
from pydantic import HttpUrl

from src.services.rss_proxy_service import get_latest_feed_item, RssProxyServiceError
from src.lib.rss_parser import parse_feed, FeedParsingError
from src.models.feed import FeedItem, CacheEntry
from src.services.cache_service import cache_service

URL = HttpUrl("https://example.com/feed.xml")
URL_STR = str(URL)

@pytest.fixture
def mock_cache_service(mocker):
    """Mocks the cache service."""
    return mocker.patch("src.services.rss_proxy_service.cache_service", autospec=True)

@pytest.fixture
def mock_parse_feed(mocker):
    """Mocks the parse_feed function."""
    return mocker.patch("src.services.rss_proxy_service.parse_feed", autospec=True)

@pytest.fixture
def sample_feed_item():
    """A sample FeedItem for consistent test results."""
    return FeedItem(
        title="Test Title",
        link=HttpUrl("https://example.com/item"),
        published_date=datetime.now(timezone.utc),
        description="Test Description"
    )

def test_get_latest_feed_item_no_cache(mock_cache_service, mock_parse_feed, sample_feed_item):
    """
    Tests the scenario where there is no cached entry for the URL.
    """
    # Arrange
    mock_cache_service.get.return_value = None
    mock_parse_feed.return_value = (sample_feed_item, "new-etag", "new-last-modified")

    # Act
    result = get_latest_feed_item(URL)

    # Assert
    assert result == sample_feed_item
    mock_cache_service.get.assert_called_once_with(URL_STR)
    mock_parse_feed.assert_called_once_with(url=URL_STR, etag=None, last_modified=None)
    mock_cache_service.set.assert_called_once()

    # Check the cached entry
    cached_entry_args = mock_cache_service.set.call_args[0]
    assert cached_entry_args[0] == URL_STR
    cached_entry = cached_entry_args[1]
    assert isinstance(cached_entry, CacheEntry)
    assert cached_entry.item == sample_feed_item
    assert cached_entry.etag == "new-etag"
    assert cached_entry.last_modified == "new-last-modified"


def test_get_latest_feed_item_cache_hit_not_modified(mock_cache_service, mock_parse_feed, sample_feed_item):
    """
    Tests the scenario where the feed has not been modified since the last fetch.
    """
    # Arrange
    cached_entry = CacheEntry(
        feed_url=URL,
        item=sample_feed_item,
        last_fetched=datetime.now(timezone.utc),
        etag="old-etag",
        last_modified="old-last-modified"
    )
    mock_cache_service.get.return_value = cached_entry
    mock_parse_feed.return_value = (None, None, None)  # Feed not modified

    # Act
    result = get_latest_feed_item(URL)

    # Assert
    assert result == sample_feed_item
    mock_cache_service.get.assert_called_once_with(URL_STR)
    mock_parse_feed.assert_called_once_with(url=URL_STR, etag="old-etag", last_modified="old-last-modified")
    mock_cache_service.set.assert_not_called()


def test_get_latest_feed_item_cache_miss_modified(mock_cache_service, mock_parse_feed, sample_feed_item):
    """
    Tests the scenario where the feed has been modified and a new item is fetched.
    """
    # Arrange
    old_item = FeedItem(title="Old Title", link=HttpUrl("https://example.com/old"), published_date=datetime.now(timezone.utc), description="Old")
    cached_entry = CacheEntry(
        feed_url=URL,
        item=old_item,
        last_fetched=datetime.now(timezone.utc),
        etag="old-etag",
        last_modified="old-last-modified"
    )
    mock_cache_service.get.return_value = cached_entry
    mock_parse_feed.return_value = (sample_feed_item, "new-etag", "new-last-modified")

    # Act
    result = get_latest_feed_item(URL)

    # Assert
    assert result == sample_feed_item
    mock_cache_service.get.assert_called_once_with(URL_STR)
    mock_parse_feed.assert_called_once_with(url=URL_STR, etag="old-etag", last_modified="old-last-modified")
    mock_cache_service.set.assert_called_once()


def test_get_latest_feed_item_fetch_fails_with_cache(mock_cache_service, mock_parse_feed, sample_feed_item):
    """
    Tests returning a stale item from cache when fetching the new one fails.
    """
    # Arrange
    cached_entry = CacheEntry(
        feed_url=URL,
        item=sample_feed_item,
        last_fetched=datetime.now(timezone.utc),
        etag="old-etag",
        last_modified="old-last-modified"
    )
    mock_cache_service.get.return_value = cached_entry
    mock_parse_feed.side_effect = FeedParsingError("Failed to parse")

    # Act
    result = get_latest_feed_item(URL)

    # Assert
    assert result == sample_feed_item
    mock_cache_service.set.assert_not_called()


def test_get_latest_feed_item_fetch_fails_no_cache(mock_cache_service, mock_parse_feed):
    """
    Tests that an error is raised when fetching fails and there's no cache.
    """
    # Arrange
    mock_cache_service.get.return_value = None
    mock_parse_feed.side_effect = FeedParsingError("Failed to parse")

    # Act & Assert
    with pytest.raises(FeedParsingError):
        get_latest_feed_item(URL)
    mock_cache_service.set.assert_not_called()


def test_get_latest_feed_item_empty_feed_no_cache(mock_cache_service, mock_parse_feed):
    """
    Tests the case of an empty feed with no prior cache. This should fail.
    """
    # Arrange
    mock_cache_service.get.return_value = None
    mock_parse_feed.return_value = (None, "new-etag", "new-last-modified") # Empty feed

    # Act & Assert
    with pytest.raises(RssProxyServiceError, match="Failed to fetch feed and no cached version available."):
        get_latest_feed_item(URL)
