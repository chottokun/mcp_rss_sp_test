import pytest
import httpx
from datetime import datetime, timezone
from pydantic import HttpUrl

from src.lib.rss_parser import parse_feed, FeedParsingError
from src.models.feed import FeedItem

# Sample RSS feed content
SAMPLE_RSS_CONTENT = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>Test RSS Feed</title>
<item>
<title>Test Item</title>
<link>https://example.com/item</link>
<description>This is a test item.</description>
<pubDate>Fri, 06 Sep 2024 10:00:00 GMT</pubDate>
</item>
</channel>
</rss>"""

@pytest.fixture
def mock_httpx_client(mocker):
    """Fixture to mock the httpx.Client."""
    client_mock = mocker.patch("httpx.Client")
    # To use the client in a 'with' statement, we need to mock the context manager methods
    instance = client_mock.return_value.__enter__.return_value
    return instance

def test_parse_valid_feed(mock_httpx_client):
    """
    Tests that a valid RSS feed is parsed correctly.
    """
    mock_response = httpx.Response(
        200,
        content=SAMPLE_RSS_CONTENT,
        headers={"ETag": "test-etag", "Last-Modified": "some-date"},
        request=httpx.Request("GET", "http://example.com/rss")
    )
    mock_httpx_client.get.return_value = mock_response

    item, etag, last_modified = parse_feed("http://example.com/rss")

    assert isinstance(item, FeedItem)
    assert item.title == "Test Item"
    assert item.link == HttpUrl("https://example.com/item")
    assert item.published_date == datetime(2024, 9, 6, 10, 0, tzinfo=timezone.utc)
    assert etag == "test-etag"
    assert last_modified == "some-date"
    mock_httpx_client.get.assert_called_once()

def test_parse_feed_not_modified(mock_httpx_client):
    """
    Tests that a 304 Not Modified response is handled correctly.
    """
    mock_response = httpx.Response(304, request=httpx.Request("GET", "http://example.com/rss"))
    mock_httpx_client.get.return_value = mock_response

    item, _, _ = parse_feed("http://example.com/rss", etag="some-etag")

    assert item is None
    mock_httpx_client.get.assert_called_once()

def test_parse_feed_http_error(mock_httpx_client):
    """
    Tests that an HTTP error raises a FeedParsingError.
    """
    mock_response = httpx.Response(500, request=httpx.Request("GET", "http://example.com/rss"))
    mock_httpx_client.get.side_effect = httpx.HTTPStatusError(
        "Server Error", request=mock_response.request, response=mock_response
    )
    with pytest.raises(FeedParsingError, match="Failed to fetch feed: HTTP 500"):
        parse_feed("http://example.com/rss")

def test_parse_bozo_feed(mock_httpx_client):
    """
    Tests that a malformed feed raises a FeedParsingError.
    """
    mock_response = httpx.Response(200, content=b"<rss><channel>", request=httpx.Request("GET", "http://example.com/rss"))
    mock_httpx_client.get.return_value = mock_response

    with pytest.raises(FeedParsingError, match="Failed to parse feed"):
        parse_feed("http://example.com/rss")
