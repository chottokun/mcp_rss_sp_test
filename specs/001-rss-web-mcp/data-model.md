# Data Models

This document defines the data structures for the RSS MCP Server feature, based on the entities identified in the specification.

## FeedItem

Represents a single item extracted from an RSS feed.

*   **Fields**:
    *   `title` (string): The title of the item.
    *   `link` (string, URL): The direct URL to the item.
    *   `published_date` (datetime): The publication date of the item.
    *   `description` (string): A summary or the full content of the item.
*   **Validation**:
    *   `link` must be a valid URL.
    *   `published_date` must be a valid datetime object.

## CacheEntry

Represents the cached data for a single RSS feed.

*   **Fields**:
    *   `feed_url` (string, URL): The original URL of the RSS feed.
    *   `item` (FeedItem): The latest `FeedItem` from the feed.
    *   `last_fetched` (datetime): The timestamp when the feed was last successfully fetched.
    *   `etag` (string, optional): The ETag header value from the last fetch, used for conditional GETs.
    *   `last_modified` (string, optional): The Last-Modified header value from the last fetch.
*   **Validation**:
    *   `feed_url` must be a valid URL.