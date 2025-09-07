# Tasks: RSS MCP Server

**Input**: Design documents from `/specs/001-rss-web-mcp/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)

## Path Conventions
- Paths assume a single project structure: `src/`, `tests/` at the repository root.

## Phase 3.1: Setup
- [ ] T001 Create the initial project directories: `src/api`, `src/lib`, `src/models`, `src/services`, `tests/contract`, `tests/integration`, `tests/unit`.
- [ ] T002 Create a `requirements.txt` file and add dependencies: `fastapi`, `uvicorn`, `feedparser`, `listparser`, `pytest`, `httpx`, `FastAPImcp`.
- [ ] T003 Configure `ruff` for linting by creating a `ruff.toml` or `pyproject.toml` file with basic rules.

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Create contract test for `POST /api/rss-proxy` in `tests/contract/test_api.py`. It must validate the request body and the expected success (200) and error (400) response schemas defined in `contracts/api.yaml`.
- [ ] T005 [P] Create integration test in `tests/integration/test_rss_proxy.py` to cover the primary user stories from `quickstart.md`. Use `httpx` to make live requests to the test RSS feed. Scenarios to test:
    1.  First request to a valid feed URL returns the latest item.
    2.  A subsequent request for the same feed returns a cached item (verify with mock or by checking response times).
    3.  A request with an invalid URL returns a 400 error.
    4.  A request for a URL that is not a valid RSS feed returns an appropriate error.

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T006 [P] Implement the `FeedItem` and `CacheEntry` Pydantic models in `src/models/feed.py` as defined in `data-model.md`.
- [ ] T007 Implement the core feed parsing logic in `src/lib/rss_parser.py`. Create a function that takes a URL, fetches the content, and uses `feedparser` to parse it and return a list of `FeedItem` objects.
- [ ] T008 Implement the caching logic in `src/services/cache_service.py`. It should use a simple in-memory dictionary to store and retrieve `CacheEntry` objects. Include methods to get, set, and check for entries.
- [ ] T009 Implement the main business logic in `src/services/rss_proxy_service.py`. This service will orchestrate the process: use `cache_service` to check for a cached item, and if it's stale or absent, use `rss_parser` to fetch and parse the feed. It must handle `ETag` and `Last-Modified` headers for efficient fetching.
- [ ] T010 Implement the `POST /api/rss-proxy` endpoint in `src/api/main.py`. This FastAPI endpoint will receive the request, call the `rss_proxy_service`, and return the appropriate HTTP response.

## Phase 3.4: Integration
- [ ] T011 Integrate `FastAPImcp` into the FastAPI application in `src/api/main.py` according to its documentation.
- [ ] T012 Add structured logging middleware to the FastAPI app to log incoming requests and outgoing responses.

## Phase 3.5: Polish
- [ ] T013 [P] Create unit tests for the feed parsing logic in `tests/unit/test_rss_parser.py`. Mock HTTP requests to test the parsing logic in isolation.
- [ ] T014 [P] Create unit tests for the caching logic in `tests/unit/test_cache_service.py` to ensure it correctly stores, retrieves, and invalidates cache entries.
- [ ] T015 Review all error handling to ensure consistent and informative error messages are returned to the client for all failure scenarios.
- [ ] T016 Create a `README.md` at the project root explaining how to set up the project, install dependencies, run the server, and run the tests.

## Dependencies
- **T001, T002, T003** (Setup) must be done first.
- **T004, T005** (Tests) must be done before Core Implementation (T006-T010).
- **T006** (Models) is a dependency for T007, T008, T009, T010.
- **T007, T008** are dependencies for **T009**.
- **T009** is a dependency for **T010**.
- Core implementation should be complete before Polish tasks.

## Parallel Example
```
# The following test and model tasks can be run in parallel:
Task: "T004 [P] Create contract test for POST /api/rss-proxy in tests/contract/test_api.py"
Task: "T005 [P] Create integration test in tests/integration/test_rss_proxy.py"
Task: "T006 [P] Implement the FeedItem and CacheEntry Pydantic models in src/models/feed.py"
```