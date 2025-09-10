from datetime import datetime, timezone
import yaml
import pytest
from fastapi.testclient import TestClient
from jsonschema import validate
from pydantic import HttpUrl

import httpx
from src.api.main import app
from src.models.feed import FeedItem
from src.services.rss_proxy_service import RssProxyServiceError
from src.lib.rss_parser import FeedParsingError

# Load the OpenAPI spec
with open("specs/001-rss-web-mcp/contracts/api.yaml", "r") as f:
    openapi_spec = yaml.safe_load(f)

client = TestClient(app)

@pytest.fixture
def mock_feed_item():
    """A sample FeedItem for consistent test results."""
    return FeedItem(
        title="Mocked Feed Title",
        link=HttpUrl("https://example.com/mocked-item"),
        published_date=datetime.now(timezone.utc),
        description="A mocked feed item description."
    )

def test_rss_proxy_contract(mocker, mock_feed_item):
    """
    Tests the POST /api/rss-proxy endpoint against its OpenAPI contract
    by mocking the service layer.
    """
    # 1. Validate Request
    request_body = {"url": "https://example.com/any-valid-url"}
    request_schema = openapi_spec["paths"]["/api/rss-proxy"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    validate(instance=request_body, schema=request_schema)

    # 2. Mock the service function
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        return_value=mock_feed_item
    )

    # 3. Make the request
    response = client.post("/api/rss-proxy", json=request_body)

    # 4. Validate Response
    assert response.status_code == 200
    response_data = response.json()

    # The returned timestamp won't be in the exact same format, so we re-parse it
    # to ensure it's a valid datetime before validation.
    if response_data.get('published_date'):
        response_data['published_date'] = datetime.fromisoformat(response_data['published_date'].replace("Z", "+00:00")).isoformat()
    else:
        # If published_date is null, remove it for validation purposes
        # as the schema expects a string.
        del response_data['published_date']


    response_schema = openapi_spec["components"]["schemas"]["FeedItem"]
    validate(instance=response_data, schema=response_schema)


def test_rss_proxy_opml_contract(mocker, mock_feed_item):
    """
    Tests the POST /api/rss-proxy endpoint with an OPML payload.
    """
    opml_content = '<opml><body><outline xmlUrl="https://example.com/mocked-item"/></body></opml>'
    request_body = {"opml": opml_content}

    # Mock the service function
    mock_get_item = mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        return_value=mock_feed_item
    )

    # Make the request
    response = client.post("/api/rss-proxy", json=request_body)

    # Validate that the service was called with the correct URL from the OPML
    mock_get_item.assert_called_once_with(HttpUrl("https://example.com/mocked-item"))

    # Validate Response
    assert response.status_code == 200
    response_data = response.json()
    response_schema = openapi_spec["components"]["schemas"]["FeedItem"]
    # We need to handle the datetime format again
    if response_data.get('published_date'):
        response_data['published_date'] = datetime.fromisoformat(response_data['published_date'].replace("Z", "+00:00")).isoformat()
    validate(instance=response_data, schema=response_schema)


def test_rss_proxy_returns_400_on_invalid_opml(mocker):
    """Tests that a 400 is returned for invalid OPML content."""
    request_body = {"opml": "<opml>not valid</opml>"}
    response = client.post("/api/rss-proxy", json=request_body)
    assert response.status_code == 400
    assert "Invalid OPML" in response.json()["detail"]


def test_rss_proxy_returns_422_with_both_url_and_opml(mocker):
    """Tests that a 422 is returned when both url and opml are provided."""
    request_body = {
        "url": "https://example.com/some-url",
        "opml": "<opml><body><outline xmlUrl=\"https://example.com/mocked-item\"/></body></opml>"
    }
    response = client.post("/api/rss-proxy", json=request_body)
    assert response.status_code == 422 # FastAPI validation error


def test_rss_proxy_returns_502_on_upstream_server_error(mocker):
    """Tests that a 502 Bad Gateway is returned if the upstream feed server fails."""
    mock_response = httpx.Response(503, request=httpx.Request("GET", "https://example.com"))
    mock_error = FeedParsingError("Upstream error")
    mock_error.__cause__ = httpx.HTTPStatusError("Service Unavailable", request=mock_response.request, response=mock_response)
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        side_effect=mock_error
    )
    response = client.post("/api/rss-proxy", json={"url": "https://example.com/bad-feed"})
    assert response.status_code == 502
    assert "Upstream server returned 503" in response.json()["detail"]


def test_rss_proxy_returns_400_on_upstream_client_error(mocker):
    """Tests that a 400 Bad Request is returned if the upstream feed is not found."""
    mock_response = httpx.Response(404, request=httpx.Request("GET", "https://example.com"))
    mock_error = FeedParsingError("Upstream error")
    mock_error.__cause__ = httpx.HTTPStatusError("Not Found", request=mock_response.request, response=mock_response)
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        side_effect=mock_error
    )
    response = client.post("/api/rss-proxy", json={"url": "https://example.com/not-found-feed"})
    assert response.status_code == 400
    assert "Could not fetch feed" in response.json()["detail"]


def test_rss_proxy_returns_400_on_feed_parsing_error(mocker):
    """Tests that a 400 Bad Request is returned for a generic feed parsing error."""
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        side_effect=FeedParsingError("Invalid feed format")
    )
    response = client.post("/api/rss-proxy", json={"url": "https://example.com/invalid-feed"})
    assert response.status_code == 400
    assert "Failed to parse feed: Invalid feed format" in response.json()["detail"]


def test_rss_proxy_returns_500_on_service_error(mocker):
    """Tests that a 500 Internal Server Error is returned for a service-level error."""
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        side_effect=RssProxyServiceError("Cache is down")
    )
    response = client.post("/api/rss-proxy", json={"url": "https://example.com/any-feed"})
    assert response.status_code == 500
    assert "Internal service error: Cache is down" in response.json()["detail"]


def test_rss_proxy_returns_500_on_unexpected_error(mocker):
    """Tests that a 500 Internal Server Error is returned for any unexpected exception."""
    mocker.patch(
        "src.api.rss_router.get_latest_feed_item",
        side_effect=Exception("Something broke")
    )
    response = client.post("/api/rss-proxy", json={"url": "https://example.com/any-feed"})
    assert response.status_code == 500
    assert "An unexpected error occurred" in response.json()["detail"]
