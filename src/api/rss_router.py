import logging
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl, model_validator
from typing import Optional
import listparser

from src.models.feed import FeedItem
from src.services.rss_proxy_service import get_latest_feed_item, RssProxyServiceError
from src.lib.rss_parser import FeedParsingError

router = APIRouter()
logger = logging.getLogger(__name__)


class RssRequest(BaseModel):
    url: Optional[HttpUrl] = None
    opml: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def check_url_or_opml(cls, data):
        if isinstance(data, dict):
            if 'url' in data and 'opml' in data:
                raise ValueError('Provide either url or opml, not both')
            if 'url' not in data and 'opml' not in data:
                raise ValueError('Either url or opml must be provided')
        return data


def get_url_from_opml(opml_string: str) -> HttpUrl:
    """Parses an OPML string and returns the first feed URL found."""
    result = listparser.parse(opml_string)
    if not result.feeds:
        raise ValueError("No feeds found in the provided OPML")
    # Return the first feed URL found
    return HttpUrl(result.feeds[0].url)


@router.post("/rss-proxy", response_model=FeedItem)
def proxy_rss_feed(request: RssRequest):
    """
    Accepts an RSS feed URL or an OPML file, fetches the latest item from
    the resolved feed, and returns it.
    It uses a cache to avoid re-fetching unchanged feeds.
    """
    target_url: HttpUrl
    if request.opml:
        try:
            target_url = get_url_from_opml(request.opml)
        except (ValueError, IndexError) as e:
            raise HTTPException(status_code=400, detail=f"Invalid OPML: {e}")
    elif request.url:
        target_url = request.url
    else:
        # This case should be prevented by the Pydantic model validator,
        # but as a safeguard:
        raise HTTPException(status_code=400, detail="No URL or OPML provided.")

    try:
        feed_item = get_latest_feed_item(target_url)
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
