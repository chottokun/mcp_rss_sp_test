# RSS MCP Server

This project is a robust FastAPI server that acts as a proxy for RSS feeds. It exposes a single endpoint to fetch the latest item from a given RSS feed URL. It is designed to be reliable, with built-in caching, robust error handling, and a mocked test suite.

The server also exposes a Model Context Protocol (MCP) endpoint at `/mcp`, allowing AI agents to interact with the RSS proxy functionality.

## Features

- **Efficient Caching**: Uses a Time-to-Live (TTL) cache (`cachetools`) to store feed items, reducing redundant requests to the source feed and improving response times.
- **Robust Error Handling**: Gracefully handles various failure scenarios, such as invalid URLs, non-feed URLs, upstream server errors (returning a 502 Bad Gateway), and malformed XML.
- **Reliable Testing**: The test suite is fast and reliable, using `respx` and `pytest-mock` to eliminate dependencies on live network services.
- **Asynchronous API**: Built with FastAPI for high performance.

## Prerequisites

- Python 3.8+
- A virtual environment (recommended)

## Setup

1.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    *On Windows, use `venv\\Scripts\\activate`*

2.  **Install dependencies**:
    The required Python packages are listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```

## Running the Server

To run the development server with live reloading:
```bash
uvicorn src.api.main:app --reload
```
The server will be available at `http://127.0.0.1:8000`. You can access the auto-generated API documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

To run the full test suite (contract, integration, and unit tests):
```bash
pytest
```
The tests are fully self-contained and do not make any live network requests.

## API Usage

Send a `POST` request to `/api/rss-proxy` with a JSON body containing the feed URL:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
  }' \
  http://127.0.0.1:8000/api/rss-proxy
```

The server will return the latest item from the feed in JSON format.
