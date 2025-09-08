from datetime import datetime, timezone
from pydantic import HttpUrl

from src.lib.rss_parser import parse_feed, FeedParsingError
from src.services.cache_service import cache_service
from src.models.feed import FeedItem, CacheEntry


class RssProxyServiceError(Exception):
    """Custom exception for the RSS Proxy service."""
    pass


def get_latest_feed_item(url: HttpUrl) -> FeedItem:
    """
    Gets the latest feed item for a given URL, using a cache to avoid
    unnecessary fetches.
    """
    url_str = str(url)
    cached_entry = cache_service.get(url_str)
    etag = cached_entry.etag if cached_entry else None
    last_modified = cached_entry.last_modified if cached_entry else None

    try:
        new_item, new_etag, new_last_modified = parse_feed(
            url=url_str, etag=etag, last_modified=last_modified
        )

        if new_item is None and cached_entry:
            return cached_entry.item

        if new_item:
            entry_to_cache = CacheEntry(
                feed_url=url,
                item=new_item,
                last_fetched=datetime.now(timezone.utc),
                etag=new_etag,
                last_modified=new_last_modified,
            )
            cache_service.set(url_str, entry_to_cache)
            return new_item

        if cached_entry:
            return cached_entry.item
        else:
            raise RssProxyServiceError("Failed to fetch feed and no cached version available.")

    except FeedParsingError as e:
        if cached_entry:
            return cached_entry.item
        raise RssProxyServiceError(str(e)) from e
