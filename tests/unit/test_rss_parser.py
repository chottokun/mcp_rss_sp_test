import pytest
import httpx
from datetime import datetime, timezone

from src.lib.rss_parser import parse_feed, FeedParsingError
from src.models.feed import FeedItem

SAMPLE_RSS_CONTENT = """
<rss version="2.0">
<channel>
  <title>Test Feed</title>
  <item>
    <title>Test Item 1</title>
    <link>http://example.com/item1</link>
    <pubDate>Sun, 07 Sep 2025 12:00:00 GMT</pubDate>
    <description>This is a test item.</description>
  </item>
</channel>
</rss>
"""

@pytest.fixture
def mock_httpx_client(mocker):
    return mocker.patch("httpx.Client")

def test_parse_feed_success(mock_httpx_client):
    mock_response = httpx.Response(
        200,
        content=SAMPLE_RSS_CONTENT,
        headers={"ETag": "new-etag"},
        request=httpx.Request("GET", "http://example.com/rss")
    )
    mock_httpx_client.return_value.__enter__.return_value.get.return_value = mock_response
    item, etag, _ = parse_feed("http://example.com/rss")
    assert isinstance(item, FeedItem)
    assert item.title == "Test Item 1"
    assert etag == "new-etag"

def test_parse_feed_not_modified(mock_httpx_client):
    mock_response = httpx.Response(304, request=httpx.Request("GET", "http://example.com/rss"))
    mock_httpx_client.return_value.__enter__.return_value.get.return_value = mock_response
    item, _, _ = parse_feed("http://example.com/rss", etag="old-etag")
    assert item is None

def test_parse_feed_http_error(mock_httpx_client):
    mock_httpx_client.return_value.__enter__.return_value.get.side_effect = httpx.RequestError("Mocked error")
    with pytest.raises(FeedParsingError, match="HTTP error"):
        parse_feed("http://example.com/rss")

def test_parse_feed_malformed(mock_httpx_client):
    mock_response = httpx.Response(200, content="<rss", request=httpx.Request("GET", "http://example.com/rss"))
    mock_httpx_client.return_value.__enter__.return_value.get.return_value = mock_response
    with pytest.raises(FeedParsingError, match="not well-formed"):
        parse_feed("http://example.com/rss")
