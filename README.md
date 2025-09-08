# RSS MCP Server

This project is a simple FastAPI server that acts as a proxy for RSS feeds. It exposes a single endpoint to fetch the latest item from a given RSS feed URL, with built-in caching to avoid unnecessary requests to the source feed.

The server also exposes a Model Context Protocol (MCP) endpoint at `/mcp`, allowing AI agents to interact with the RSS proxy functionality.

## Setup

1.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

To run the development server with live reloading:
```bash
uvicorn src.api.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`.

## Running Tests

To run the full test suite (contract, integration, and unit tests):
```bash
pytest
```

## API Usage

Send a `POST` request to `/api/rss-proxy` with a JSON body containing the feed URL:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
  }' \
  http://127.0.0.1:8000/api/rss-proxy
```

The server will return the latest item from the feed.
