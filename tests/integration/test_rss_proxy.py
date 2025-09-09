import pytest
import respx
from fastapi.testclient import TestClient
from httpx import Response

from src.api.main import app

client = TestClient(app)

VALID_RSS_URL = "https://example.com/valid-rss.xml"
NOT_A_FEED_URL = "https://example.com/not-a-feed"
INVALID_URL = "not-a-valid-url"
SERVER_ERROR_URL = "https://example.com/server-error"

# A sample RSS feed content for mocking
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

@respx.mock
def test_first_request_to_valid_feed():
    """
    Scenario: First request to a valid feed URL.
    Expected: Returns 200 OK and feed data.
    """
    respx.get(VALID_RSS_URL).mock(return_value=Response(200, content=SAMPLE_RSS_CONTENT))
    response = client.post("/api/rss-proxy", json={"url": VALID_RSS_URL})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["link"] == "https://example.com/item"

def test_request_with_invalid_url():
    """
    Scenario: A request with an invalid URL format.
    Expected: Returns 422 Unprocessable Entity.
    """
    response = client.post("/api/rss-proxy", json={"url": INVALID_URL})
    assert response.status_code == 422

@respx.mock
def test_request_with_non_feed_url():
    """
    Scenario: A request for a URL that points to a non-feed page.
    Expected: Returns 400 Bad Request with a specific error message.
    """
    respx.get(NOT_A_FEED_URL).mock(return_value=Response(200, text="This is not a feed."))
    response = client.post("/api/rss-proxy", json={"url": NOT_A_FEED_URL})
    assert response.status_code == 400
    assert "Failed to parse feed" in response.json()["detail"]

@respx.mock
def test_request_to_url_with_server_error():
    """
    Scenario: The target URL returns a server error.
    Expected: Returns 502 Bad Gateway.
    """
    respx.get(SERVER_ERROR_URL).mock(return_value=Response(500))
    response = client.post("/api/rss-proxy", json={"url": SERVER_ERROR_URL})
    assert response.status_code == 502
    assert "Could not fetch feed" in response.json()["detail"]
