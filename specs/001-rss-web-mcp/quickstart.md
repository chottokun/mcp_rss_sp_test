# Quickstart Guide

This guide provides quick steps to test the RSS MCP Server using `curl`.

## Prerequisites

The server must be running locally.

## Fetching from an RSS Feed URL

This scenario corresponds to the primary user story of fetching the latest item from a single RSS feed.

**Command:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d 
  {
    "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
  }
  http://127.0.0.1:8000/api/rss-proxy
```

**Expected Success Response (`200 OK`):**
A JSON object representing the latest feed item.
```json
{
  "title": "Some News Title",
  "link": "https://news.yahoo.co.jp/pickup/",
  "published_date": "...",
  "description": "..."
}
```

## Error: Invalid URL

**Command:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d 
  {
    "url": "not-a-valid-url"
  }
  http://127.0.0.1:8000/api/rss-proxy
```

**Expected Error Response (`400 Bad Request`):**
```json
{
  "detail": "Invalid URL provided"
}
```
