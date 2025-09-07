# Feature Specification: RSSからWeb更新データを入手するMCPサーバー

**Feature Branch**: `001-rss-web-mcp`
**Created**: 2025-09-07
**Status**: Draft
**Input**: User description: "RSSからWeb更新データを入手するMCPサーバー。引数としてRSS FeedのURLもしくは、OPMLファイル（の中身）を与える。配信サーバーに負担にならないように更新を確認し、更新がない場合はキャッシュしたデータを与える。キャッシュは、最新の１件だけでよい。"

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a client, I want to provide an RSS feed URL or an OPML file to an MCP server, so that I can receive the latest update from the feed without directly and repeatedly querying the source.

### Acceptance Scenarios
1. **Given** a client provides a valid RSS feed URL, **When** the server processes the request for the first time, **Then** the server fetches the feed, returns the latest item, and caches it.
2. **Given** a client provides the same RSS feed URL again and there are no new updates, **When** the server processes the request, **Then** the server returns the cached item without re-fetching the feed from the source.
3. **Given** a client provides the same RSS feed URL again and there is a new update, **When** the server processes the request, **Then** the server fetches the feed, returns the new latest item, and updates the cache with the new item.
4. **Given** a client provides the content of a valid OPML file, **When** the server processes the request, **Then** the server identifies the RSS feed URLs within it, and for each feed, returns the latest item, caching it individually. [NEEDS CLARIFICATION: How should the server return items from multiple feeds in an OPML file? As a single aggregated list or a structured response?]

### Edge Cases
- What happens when the provided URL is not a valid RSS feed? The system should return a clear error message.
- What happens when the provided content is not a valid OPML file? The system should return a clear error message.
- What happens when the RSS feed source is unavailable or returns an error? The system should return a cached version if available, otherwise an error. [NEEDS CLARIFICATION: What should the specific error message be? Should it retry?]
- How does the system handle feeds with no items? The system should return an empty or appropriate response.

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The system MUST accept an RSS feed URL as an input parameter.
- **FR-002**: The system MUST accept OPML file content as an input parameter.
- **FR-003**: The system MUST parse the provided RSS feed to extract its items.
- **FR-004**: The system MUST parse the provided OPML content to extract RSS feed URLs.
- **FR-005**: The system MUST identify the single most recent item from a feed based on its publication date or order in the feed.
- **FR-006**: The system MUST cache the single most recent item from a successfully fetched feed.
- **FR-007**: On subsequent requests for the same feed, the system MUST check for updates from the source in an efficient manner (e.g., using HTTP headers like ETag or Last-Modified).
- **FR-008**: If no update is found on the source feed, the system MUST return the item from its cache.
- **FR-009**: If an update is found, the system MUST fetch the new data, update the cache with the new latest item, and return it.
- **FR-010**: The system MUST handle invalid RSS feed URLs and OPML content by returning an appropriate error.
- **FR-011**: The test suite MUST use the following URL for validation: `https://news.yahoo.co.jp/rss/topics/top-picks.xml`

### Key Entities *(include if feature involves data)*
- **FeedItem**: Represents a single item from an RSS feed. Key attributes: Title, Link, Publication Date, Description.
- **CacheEntry**: Represents the cached data for a specific feed URL. Key attributes: Feed URL, Cached FeedItem, Last Fetched Timestamp.

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---