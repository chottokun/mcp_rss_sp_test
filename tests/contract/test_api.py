import yaml
import pytest
from fastapi.testclient import TestClient
from jsonschema import validate

from src.api.main import app

# Load the OpenAPI spec
with open("specs/001-rss-web-mcp/contracts/api.yaml", "r") as f:
    openapi_spec = yaml.safe_load(f)

client = TestClient(app)

def test_rss_proxy_contract():
    """
    Tests the POST /api/rss-proxy endpoint against its OpenAPI contract.
    """
    request_body = {"url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"}
    request_schema = openapi_spec["paths"]["/api/rss-proxy"]["post"]["requestBody"]["content"]["application/json"]["schema"]
    validate(instance=request_body, schema=request_schema)

    response = client.post("/api/rss-proxy", json=request_body)

    assert response.status_code == 200

    response_schema = openapi_spec["components"]["schemas"]["FeedItem"]
    validate(instance=response.json(), schema=response_schema)
