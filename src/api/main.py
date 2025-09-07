import logging
import time
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from fastapi_mcp import FastApiMCP

from src.models.feed import FeedItem
from src.services.rss_proxy_service import get_latest_feed_item, RssProxyServiceError

app = FastAPI(
    title="RSS MCP Server",
    version="0.1.0",
    description="A server to proxy RSS feeds and provide the latest item.",
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"request_path={request.url.path} method={request.method} status_code={response.status_code} duration={process_time:.4f}s"
    )
    return response

class RssRequest(BaseModel):
    url: HttpUrl

@app.post("/api/rss-proxy", response_model=FeedItem)
def proxy_rss_feed(request: RssRequest):
    """
    Accepts an RSS feed URL, fetches the latest item, and returns it.
    It uses a cache to avoid re-fetching unchanged feeds.
    """
    try:
        feed_item = get_latest_feed_item(request.url)
        return feed_item
    except RssProxyServiceError as e:
        error_str = str(e).lower()
        if "validation failed" in error_str or "missing a publication date" in error_str:
            raise HTTPException(status_code=422, detail=f"Invalid data in source feed: {e}")

        if "not well-formed" in error_str or "no entries" in error_str:
            raise HTTPException(status_code=404, detail=f"Could not parse feed: {e}")

        if "http error" in error_str:
            raise HTTPException(status_code=404, detail=f"Could not fetch feed: {e}")

        raise HTTPException(status_code=500, detail=f"Internal server error while processing feed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# Mount the MCP server
mcp = FastApiMCP(app)
mcp.mount()
