# Implementation Plan: RSS MCP Server

**Branch**: `001-rss-web-mcp` | **Date**: 2025-09-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rss-web-mcp/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
4. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, or `GEMINI.md` for Gemini CLI).
6. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
7. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
8. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
This plan outlines the implementation of an MCP (Managed Component Proxy) server for RSS feeds. The server will accept an RSS feed URL or OPML data, fetch the latest item, and cache it. Subsequent requests will be served from the cache if no updates are available, minimizing load on the source server. The implementation will use Python with FastAPI and FastAPImcp.

## Technical Context
**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, FastAPImcp, feedparser, listparser
**Storage**: In-memory Python dictionary for caching
**Testing**: pytest
**Target Platform**: Linux server
**Project Type**: single project
**Performance Goals**: p99 response time <500ms for cached items.
**Constraints**: Must use ETag and/or Last-Modified headers to avoid re-downloading unchanged feeds.
**Scale/Scope**: Designed to handle approximately 100 unique feed URLs with moderate request volume.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: [1] (api)
- Using framework directly? Yes
- Single data model? Yes
- Avoiding patterns? Yes, starting with a simple service class.

**Architecture**:
- EVERY feature as library? Yes, the core logic will be a self-contained service.
- Libraries listed: `rss_mcp_lib`: Fetches, parses, and caches RSS feeds.
- CLI per library: A simple CLI for testing the library directly.
- Library docs: Not planned for this stage.

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→Unit will be followed.
- Real dependencies used? Yes, live RSS feed for integration tests.
- Integration tests for: new library, contract changes.
- FORBIDDEN: Implementation before test, skipping RED phase.

**Observability**:
- Structured logging included? Yes, using standard Python logging.
- Frontend logs → backend? N/A
- Error context sufficient? Yes, will include feed URL in error logs.

**Versioning**:
- Version number assigned? 0.1.0
- BUILD increments on every change? No, manual increments for now.
- Breaking changes handled? N/A for initial version.

## Project Structure

### Documentation (this feature)
```
specs/001-rss-web-mcp/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── api/
└── lib/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Option 1: Single project

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context**: None. The technical context is defined.
2. **Generate and dispatch research agents**: No research needed as the path is clear.
3. **Consolidate findings** in `research.md`.

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`.
2. **Generate API contracts** from functional requirements → `/contracts/`.
3. **Generate contract tests** from contracts.
4. **Extract test scenarios** from user stories → `quickstart.md`.
5. **Update agent file incrementally**.

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `/templates/tasks-template.md` as base.
- Generate tasks from Phase 1 design docs.
- Each contract endpoint → contract test task [P].
- Each data model entity → model creation task [P].
- Each user story → integration test task.
- Implementation tasks to make tests pass.

**Ordering Strategy**:
- TDD order: Tests before implementation.
- Dependency order: Models → Library → API.
- Mark [P] for parallel execution.

**Estimated Output**: ~15-20 tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md)
**Phase 5**: Validation (run tests, execute quickstart.md)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       | N/A        | N/A                                 |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [ ] Complexity deviations documented

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*