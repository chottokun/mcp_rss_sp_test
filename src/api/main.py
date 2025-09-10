import logging
import time
import httpx
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from fastapi_mcp.server import add_mcp_server

from src.api import rss_router
from src.models.feed import FeedItem
from src.services.rss_proxy_service import get_latest_feed_item, RssProxyServiceError
from src.lib.rss_parser import FeedParsingError

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


app.include_router(rss_router.router, prefix="/api")

# Mount the MCP server
add_mcp_server(app)
