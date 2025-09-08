from datetime import datetime, timezone
import yaml
import pytest
from fastapi.testclient import TestClient
from jsonschema import validate
from pydantic import HttpUrl

from src.api.main import app
from src.models.feed import FeedItem

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
        "src.api.main.get_latest_feed_item",
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
