from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import Optional


class FeedItem(BaseModel):
    title: str
    link: HttpUrl
    published_date: datetime
    description: str


class CacheEntry(BaseModel):
    feed_url: HttpUrl
    item: FeedItem
    last_fetched: datetime
    etag: Optional[str] = None
    last_modified: Optional[str] = None
