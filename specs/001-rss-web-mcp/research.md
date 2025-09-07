# Research & Decisions

This document records the technical decisions made during the planning phase for the RSS MCP Server feature.

## Technical Stack

*   **Decision**: Use Python 3.11 with FastAPI.
*   **Rationale**: The user specified this stack. FastAPI is a modern, high-performance web framework for Python that is easy to learn and use.
*   **Alternatives considered**: None, as the stack was specified.

## Core Dependencies

*   **Decision**:
    *   `FastAPImcp`: For MCP integration.
    *   `feedparser`: For robust RSS/Atom feed parsing.
    *   `listparser`: For parsing OPML files.
*   **Rationale**: These are standard and well-maintained libraries in the Python ecosystem for their respective tasks. `feedparser` handles many complexities of feed formats automatically. `listparser` is designed specifically for OPML.
*   **Alternatives considered**: Custom XML parsing, but this is error-prone and time-consuming.

## Caching Strategy

*   **Decision**: Use a simple in-memory Python dictionary.
*   **Rationale**: The requirement is to cache only the single latest item per feed. A global dictionary mapping feed URLs to cache entries is sufficient and avoids introducing external dependencies like Redis for this simple use case.
*   **Alternatives considered**: Redis, but this would add unnecessary complexity for the current requirements.

## Testing

*   **Decision**: Use `pytest`.
*   **Rationale**: `pytest` is the de-facto standard for testing in Python, with a rich ecosystem of plugins and a simple, powerful assertion syntax.
*   **Alternatives considered**: `unittest` (built-in), but `pytest` is generally considered more productive.