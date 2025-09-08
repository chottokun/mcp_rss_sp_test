import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

VALID_RSS_URL = "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
INVALID_URL = "not-a-valid-url"
NOT_A_FEED_URL = "https://example.com"

def test_first_request_to_valid_feed():
    """
    Scenario: First request to a valid feed URL.
    Expected: Returns 200 OK.
    """
    response = client.post("/api/rss-proxy", json={"url": VALID_RSS_URL})
    assert response.status_code == 200
    assert "title" in response.json()

def test_request_with_invalid_url():
    """
    Scenario: A request with an invalid URL.
    Expected: Returns 422 Unprocessable Entity.
    """
    response = client.post("/api/rss-proxy", json={"url": INVALID_URL})
    assert response.status_code == 422

def test_request_with_non_feed_url():
    """
    Scenario: A request for a URL that is not a valid RSS feed.
    Expected: Returns 404 Not Found.
    """
    response = client.post("/api/rss-proxy", json={"url": NOT_A_FEED_URL})
    assert response.status_code == 404
