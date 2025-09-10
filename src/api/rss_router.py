import logging
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from src.models.feed import FeedItem
from src.services.rss_proxy_service import get_latest_feed_item, RssProxyServiceError
from src.lib.rss_parser import FeedParsingError

router = APIRouter()
logger = logging.getLogger(__name__)

class RssRequest(BaseModel):
    url: HttpUrl

@router.post("/rss-proxy", response_model=FeedItem)
def proxy_rss_feed(request: RssRequest):
    """
    Accepts an RSS feed URL, fetches the latest item, and returns it.
    It uses a cache to avoid re-fetching unchanged feeds.
    """
    try:
        feed_item = get_latest_feed_item(request.url)
        return feed_item
    except FeedParsingError as e:
        # Check if the cause is an HTTP error from the target server
        if isinstance(e.__cause__, httpx.HTTPStatusError):
            status_code = e.__cause__.response.status_code
            if 500 <= status_code < 600:
                # The dependency is down, so it's a Bad Gateway
                raise HTTPException(status_code=502, detail=f"Could not fetch feed: Upstream server returned {status_code}")
            else:
                # Any other HTTP error (like 404) is treated as a client error
                raise HTTPException(status_code=400, detail=f"Could not fetch feed: {e}")
        # This occurs when the fetched content is not a valid feed
        raise HTTPException(status_code=400, detail=f"Failed to parse feed: {e}")
    except RssProxyServiceError as e:
        # This occurs for other service-level issues
        raise HTTPException(status_code=500, detail=f"Internal service error: {e}")
    except Exception as e:
        logger.error("An unexpected error occurred", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
