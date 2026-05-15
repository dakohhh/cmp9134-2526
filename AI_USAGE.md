# AI Usage Log

Tool: Claude Code (claude-sonnet-4-6) via Claude Code CLI
Purpose: Development assistance for CMP9134 Robot Management System

---

## Session 1 — 2026-05-12

### Entry 1
**Task Category:** Codebase Audit & Gap Analysis
**Prompt Summary:** Asked Claude to explore the full codebase and answer: what stack is being used, what is done so far, and what is missing relative to the assessment brief.
**Why:** Needed a structured overview of the project state before continuing development.
**Outcome:** Accepted. Claude identified the full module structure (auth, robot, map, audit_log, socket, admin, token, user), confirmed the stack (FastAPI + SQLModel + React + Docker), and flagged 5 gaps: missing tests, no CI/CD, admin router not registered in main.py, connection status not displayed in dashboard UI, and repo not yet public.
**Verified:** Manually confirmed each gap by reading the relevant files — admin router absence confirmed in main.py, connectionStatus confirmed unused in dashboard.tsx.

### Entry 2
**Task Category:** Assessment Brief Analysis
**Prompt Summary:** Uploaded the assessment brief PDF and asked Claude to cross-reference it against the existing codebase to identify what is missing.
**Why:** Needed a precise checklist of required artefact features vs what was built.
**Outcome:** Accepted. Produced a gap analysis table. Confirmed that robot navigation service and JWT auth system were written independently (not AI-generated).
**Verified:** Review confirmed the analysis was accurate. Corrected Claude's assumption that robot/service.py and the auth system were AI-assisted — both were written manually.

### Entry 3
**Task Category:** Frontend API Type Update & UI Fix
**Prompt Summary:** API response for audit logs was updated to include `user.full_name` nested object. Asked Claude to update the TypeScript type in `audit-log.ts` and change the table column from showing truncated `user_id` to showing `user.full_name`.
**Why:** Boilerplate type update and table cell change — existing UI was showing raw UUIDs instead of human-readable names.
**Outcome:** Accepted. Added `AuditLogUserV1` interface, added `user` field to `AuditLogEntryV1`, updated table header to "User", updated cell to render `entry.user?.full_name` with UUID fallback.
**Verified:** Confirmed the API response shape matches the new type. Fallback to truncated UUID handles any entries where `full_name` is null.

### Entry 4
**Task Category:** Bug Fix — Admin Router Not Registered
**Prompt Summary:** Asked Claude to add the admin router to main.py if it was missing.
**Why:** The admin endpoint (`POST /api/v1/admin/user/{id}/role`) existed but was unreachable because it was never registered with the FastAPI app, meaning RBAC role promotion could not be demonstrated.
**Outcome:** Accepted. Added import and `app.include_router(admin_router)` call to `register_routers` in main.py.
**Verified:** Confirmed the import path (`app.admin.router`) matches the file structure and that the router variable name is correct. Endpoint is now reachable.

### Entry 5
**Task category:** Frontend UX — telemetry WebSocket connection state  
**AI tool / model:** Cursor in-editor agent (Auto); *exact foundation model varies by Cursor plan — note the model name shown in your Cursor UI when you copy this into the university Appendix A table.*  
**Prompt summary:** Implement dashboard copy for telemetry link health: explicit “Connecting…”, “Reconnecting…”, and “Signal lost” (assessment brief: visual indicators when the stream drops / reconnects). Update `AI_USAGE.md` with what was implemented, why, acceptance/rejection, and verification.  
**Why implemented:** The hook already tracked `connectionStatus` but the UI did not surface it, so operators could not see at a glance whether live data was stale due to a dropped WebSocket. Separating **first connect** vs **reconnect after a successful session** avoids showing “Reconnecting…” on the initial page load.  
**Outcome:** **Accepted** (with edits below).  
- **Accepted from AI:** Header “Telemetry link” chip with `role="status"` / `aria-live="polite"`, colour-coded styles (live / warning / lost), and short supporting line (“Opening telemetry stream”, “Restoring…”, “Retrying connection automatically”).  
- **Modified / added manually:** Extended `ConnectionStatus` with `'reconnecting'` and `hadSuccessfulConnectionRef` in `useRobotTelemetry.ts` so “Reconnecting…” only appears after a prior successful connection, not on first load.  
- **Rejected / not done:** No toast library or modal alerts (kept inline header indicator to match existing dashboard density); no change to backend robot HTTP retry logic (out of scope for this task).  
**Verified:** Read `useRobotTelemetry.ts` and `dashboard.tsx` after edit; confirmed `connectionStatus` is consumed in the dashboard; ran `npm run build` — build stopped on pre-existing `tsconfig.json` TS5103 (`ignoreDeprecations`), not on these files; manual browser check recommended: stop robot container → expect “Signal lost” then “Reconnecting…”.

### Entry 5
**Task Category:** Verification — Connection Status Indicator
**Prompt Summary:** Asked Claude to add a "Reconnecting…" / "Signal Lost" banner to the dashboard, then asked if it was already there.
**Why:** Brief explicitly requires visual indicators for telemetry connection state.
**Outcome:** Rejected (not needed). Code was already fully implemented by the student — `telemetryLinkPresentation` function, `connectionStatus` destructured from hook, and the indicator rendered in the header at line 180 of dashboard.tsx. Claude confirmed it was complete with no changes needed.
**Verified:** Grep confirmed `connectionStatus`, `reconnecting`, `Signal lost`, and `linkUi` were all present and wired up correctly.

### Entry 6
**Task Category:** Test Boilerplate — Auth API Tests
**Prompt Summary:** Asked Claude to provide boilerplate for the remaining auth API endpoint happy-path tests (session, logout, refresh-token) after manually writing register and login tests.
**Why:** Needed the correct way to pass Bearer tokens in headers and handle cookie-based refresh tokens with TestClient.
**Outcome:** Accepted with review. Claude read the auth router to confirm the 5 endpoints and generated test functions for `test_get_session_v1`, `test_logout_v1`, and `test_refresh_token_v1`. Verified that `access_token` is extracted correctly from `login_response.json()["data"]["access_token"]` matching the actual API response shape. Confirmed TestClient handles cookies automatically so refresh-token and logout tests don't need manual cookie handling.
**Verified:** Checked the auth router to confirm endpoint paths, HTTP methods, and that refresh_token comes from Cookie() — matching how the tests are written.

### Entry 7
**Task Category:** Bug Fix — Refresh Token Test Returning 401
**Prompt Summary:** Asked Claude to debug `test_refresh_token_v1` which was consistently returning 401 despite register and login succeeding.
**Why:** Could not determine why the refresh-token call was failing — all prior debug attempts (checking DB session visibility, adding debug prints) had not identified the root cause.
**Outcome:** Accepted. Claude traced the full auth flow and identified that the test was calling `/v1/auth/refresh-token/` with a trailing slash. FastAPI's `redirect_slashes=True` issued a 307 redirect, and httpx (which backs TestClient) does not forward per-request `cookies=` on redirects — only its persistent cookie jar. So `refresh_token` arrived as `None` and the first guard in `AuthService.refresh_token` raised `UnauthorizedException`. Fix was to remove the trailing slash. Register and login were unaffected because they pass data in the JSON body, which IS forwarded on a 307.
**Verified:** Read `auth/router.py` to confirm the route is declared without trailing slash (`/refresh-token`). Confirmed that logout also uses a cookie and would have the same issue — trailing slashes removed from those calls too.

### Entry 8
**Task Category:** Test Boilerplate — Remaining Auth Happy-Path Tests
**Prompt Summary:** Asked Claude to implement the remaining happy-path test cases for the auth API (`test_get_session_v1` and `test_logout_v1`).
**Why:** Two of the five auth endpoints (session, logout) had no test coverage.
**Outcome:** Accepted. Claude added `test_get_session_v1` (registers, logs in, calls GET /v1/auth/session with Bearer token, asserts 200) and `test_logout_v1` (registers, logs in, calls POST /v1/auth/logout with both Bearer header and refresh_token cookie, asserts 200). No trailing slashes used on cookie/header-dependent calls.
**Verified:** Checked auth router to confirm `logout` requires both `auth_bearer` (access token) and `Cookie()` (refresh token), matching how the test is written.

### Entry 9
**Task Category:** Test Boilerplate — Happy-Path Tests for All Remaining Modules
**Prompt Summary:** Asked Claude to implement all happy-path API test cases for every remaining module (audit-log, admin, robot, map) and add a `commander_tokens` fixture to support COMMANDER-role tests.
**Why:** Needed test coverage across all endpoints to satisfy the brief's automated testing requirement. Required understanding of how to create a COMMANDER user for tests (no public endpoint exists for self-promotion), how to mock the external robot API and Redis lock, and how to get a target user's ID via the session endpoint for the admin role test.
**Outcome:** Accepted. Claude added:
- `commander_tokens` async fixture in conftest.py: registers a user with a unique email, directly promotes to COMMANDER via the test DB session (bypassing the API), then logs in and returns the token dict.
- `tests/api/test_audit_log.py`: `test_get_all_audit_logs_v1` — calls GET /v1/audit-log/ with Commander token.
- `tests/api/test_admin.py`: `test_update_user_role_v1` — registers a target user, gets their ID via /v1/auth/session, then calls POST /v1/admin/user/{id}/role.
- `tests/api/test_map.py`: `test_get_map_v1` — patches `httpx.AsyncClient` to return a fake 20×20 grid response, calls GET /v1/map/.
- `tests/api/test_robot.py`: `test_move_robot_v1` and `test_reset_robot_v1` — patches both `app.robot.service.redis_from_url` (to return a mock Redis that grants the lock) and `httpx.AsyncClient` (to return fake robot status/move responses).
**Verified:** Read all routers and services before writing tests to confirm endpoint paths, auth requirements (auth_bearer vs require_permission), and which external dependencies (Redis, robot HTTP API) needed mocking. Confirmed `CacheService.redis` is None when Redis is unavailable, which causes `move_robot` to call `redis_from_url` directly — hence patching at `app.robot.service.redis_from_url`.

### Entry 10
**Task Category:** Integration Tests — Real Robot Container
**Prompt Summary:** Asked Claude to generate integration tests that hit the real robot container and Redis, and add the entry to AI_USAGE.md.
**Why:** Assessment brief requires tests against the real robot simulator, not just mocked ones. API tests use mocks for speed and isolation; integration tests prove the full stack works end-to-end.
**Outcome:** Accepted. Claude:
- Created `tests/integration/__init__.py`, `tests/integration/conftest.py`, and `tests/integration/test_robot.py`
- `tests/integration/conftest.py` — self-sufficient: own `setup_db`, `commander_tokens`, and `client` fixture with no mocks (real Redis and robot HTTP client used)
- `tests/integration/test_robot.py` — three tests: `test_get_map_integration` (GET /v1/map/, asserts width/height/grid shape), `test_move_robot_integration` (POST /v1/robot/move/ RIGHT, then verifies a COMMAND audit log entry), `test_reset_robot_integration` (POST /v1/robot/reset/, then verifies a RESET_ROBOT audit log entry)
- Updated `docker-compose-test.yaml` to add `redis` and `robot` services alongside the existing `test_db`
- Moved `tests/conftest.py` content into `tests/api/conftest.py` (API-specific mocks belong there), making each test suite self-contained
- Run with: `docker compose -f docker-compose-test.yaml up -d && poetry run pytest tests/integration/ -v`
- Registered `integration` custom marker in `pyproject.toml` to silence `PytestUnknownMarkWarning`
**Verified:** API test suite (11 tests) still passes after the conftest reorganisation. Integration tests (3 tests) pass against live services. Marker warning resolved.

### Entry 11
**Task Category:** Documentation — Project README
**Prompt Summary:** Asked Claude to create a README for the project including setup instructions using docker-compose.yaml and all relevant project information, and to add the prompt to AI_USAGE.md.
**Why:** The assessment requires a public GitHub repository with documentation. The README serves as the entry point for anyone (including the assessor) cloning the repo.
**Outcome:** Accepted. Claude read docker-compose.yaml, Dockerfile, entrypoint.sh, Makefile, and pyproject.toml to produce a README covering: stack table, feature list, Docker quick start, local development setup, environment variables reference, testing instructions (unit/API/integration), CI/CD summary, and project structure tree.
**Verified:** Read the generated file and confirmed all ports, service names, commands, and paths match the actual project configuration.

---

## Notes
- Robot navigation logic (robot/service.py) — written manually, not AI-generated
- JWT auth system (token/, auth/service.py) — written manually, not AI-generated
- Entries below will be added as AI assistance is used going forward
