---

description: "Implementation tasks for API endpoint test coverage"
---

# Tasks: API Endpoint Test Coverage

**Input**: Design documents from `specs/001-api-endpoint-tests/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [endpoint-coverage.md](contracts/endpoint-coverage.md),
and [quickstart.md](quickstart.md)

**Tests**: This feature explicitly requests automated endpoint tests. Preserve
existing application behavior; report contract discrepancies rather than
silently changing the application.

## Phase 1: Setup

**Purpose**: Establish a clean baseline with existing tooling.

- [X] T001 Run the existing baseline `python -m pytest tests/integration` using `tests/integration/` and record any pre-existing failures before making changes.
- [X] T002 Inspect existing `tests/integration/test_api.py` and `tests/integration/test_health.py` to identify reusable scenarios and avoid duplicating them.

---

## Phase 2: Foundational

**Purpose**: Provide isolated, reusable test infrastructure for every story.

- [X] T003 Extract or introduce a function-scoped client and isolated mongomock database fixture in `tests/integration/conftest.py`; override the actual database dependency, initialize supported indexes, provide a test-only signing secret, and close clients and restore overrides and settings on teardown.
- [X] T004 Prevent process-local rate-limit counters from leaking between cases in `tests/integration/conftest.py` without disabling rate-limit behavior for tests that exercise it; migrate the existing fixture in `tests/integration/test_api.py` to use the shared fixture.
- [X] T005 Add reusable helpers for two test accounts, token pairs, owned todos and comments in `tests/integration/conftest.py`; use valid values per [data-model.md](data-model.md), `Test account.email`, `Test account.name`, `Test account.password`, `Todo.title`, `Todo.description`, `Todo.status`, and `Comment.body`.
- [X] T006 Run the existing tests in `tests/integration/test_api.py` and `tests/integration/test_health.py` after fixture changes and resolve fixture regressions without altering production behavior.

**Checkpoint**: Isolated test fixtures are usable by each story.

---

## Phase 3: User Story 1 - Verify every existing endpoint (Priority: P1)

**Goal**: Provide a successful response and state assertion for every inventoried endpoint.

**Independent Test**: Run the success scenarios and confirm that all 17 rows in
`contracts/endpoint-coverage.md` identify a passing test.

### Tests and implementation for User Story 1

- [X] T007 [P] [US1] Verify the health response for `GET /api/health` in `tests/integration/test_health.py`.
- [X] T008 [P] [US1] Add or extend successful register, login, and refresh rotation tests in `tests/integration/test_auth_endpoints.py`, asserting user and token response fields and refresh-token state.
- [X] T009 [P] [US1] Test `GET` and `PATCH /api/users/me` in `tests/integration/test_user_endpoints.py`, asserting profile identity, no password hash, and persisted name changes.
- [X] T010 [P] [US1] Test todo create, list, read, update, and delete success in `tests/integration/test_todo_endpoints.py`, asserting response fields, ownership, persisted changes, and deletion.
- [X] T011 [P] [US1] Test comment create, list, update, and delete success in `tests/integration/test_comment_endpoints.py`, including persistence and comment removal when the parent todo is deleted.
- [X] T012 [P] [US1] Test activity listing and retrieval in `tests/integration/test_activity_endpoints.py`, asserting relevant recorded actions, owner, pagination, and todo filtering.
- [X] T013 [US1] Add concrete success-test identifiers for all 17 endpoints to `specs/001-api-endpoint-tests/contracts/endpoint-coverage.md` and run the success tests in `tests/integration/`.

**Checkpoint**: The successful behavior of each endpoint is independently verifiable.

---

## Phase 4: User Story 2 - Verify invalid and unauthorized requests (Priority: P2)

**Goal**: Verify rejected credentials, invalid inputs, missing resources, and
user isolation without unintended state changes.

**Independent Test**: Run negative tests and inspect the mapping for each
applicable endpoint and scenario, including missing and invalid credentials on
every protected method/path.

### Tests and implementation for User Story 2

- [X] T014 [P] [US2] Add parameterized missing and invalid bearer credential cases for every protected method/path in `tests/integration/test_authentication_matrix.py`; verify rejection and unchanged state for mutations, including expired and refresh-purpose access credentials.
- [X] T015 [P] [US2] Add registration, login, and refresh failure cases in `tests/integration/test_auth_errors.py`, including duplicate email, invalid credentials, expired and wrong-purpose refresh tokens, and reuse; use deterministic timestamps and cite [data-model.md](data-model.md) for `Test account.email`, `Test account.name`, and `Test account.password`.
- [X] T016 [P] [US2] Add invalid profile-update boundary cases and current-user isolation in `tests/integration/test_user_errors.py`, citing [data-model.md](data-model.md) for `Test account.name` and verifying rejected mutations do not persist.
- [X] T017 [P] [US2] Add todo validation, missing/malformed/absent ID, and cross-user read/update/delete cases in `tests/integration/test_todo_errors.py`; cite [data-model.md](data-model.md) for `Todo.title`, `Todo.description`, and `Todo.status`, and verify unchanged state after rejection.
- [X] T018 [P] [US2] Add invalid comment body, parent/comment ID, and cross-user list/create/update/delete cases in `tests/integration/test_comment_errors.py`; cite [data-model.md](data-model.md) for `Comment.body` and verify rejected mutations leave data unchanged.
- [X] T019 [P] [US2] Add activity missing/malformed/absent ID and cross-user list/read cases in `tests/integration/test_activity_errors.py`, including non-disclosure of another user's records.
- [X] T020 [P] [US2] Add empty-list, valid boundary, invalid `page` and `page_size` cases for todo, comment, and activity lists in `tests/integration/test_pagination.py`, citing [data-model.md](data-model.md) for `Scenario.page` and `Scenario.page_size`; verify activity todo-filter behavior.
- [X] T021 [US2] Record concrete negative, credential, and ownership test identifiers or explicit not-applicable reasons for all rows in `specs/001-api-endpoint-tests/contracts/endpoint-coverage.md`, then run all negative scenarios in `tests/integration/`.

**Checkpoint**: All applicable error and isolation scenarios are mapped and pass.

---

## Phase 5: User Story 3 - Make results repeatable and understandable (Priority: P3)

**Goal**: Enable contributors to run isolated tests repeatedly and identify failures.

**Independent Test**: Follow the documented steps twice and verify both runs
pass with no manual cleanup; a failed test identifies its endpoint and scenario.

### Tests and implementation for User Story 3

- [X] T022 [US3] Verify fixture teardown and independent test data across repeated tests in `tests/integration/test_isolation.py`, including restoration of database overrides and settings.
- [X] T023 [US3] Ensure pytest names and parameter IDs in `tests/integration/` identify endpoint, method, and scenario so failures show expected and actual outcomes.
- [X] T024 [US3] Update prerequisites, isolated data setup, cleanup, and test commands in `README.md` and `specs/001-api-endpoint-tests/quickstart.md`, noting that mongomock does not verify real MongoDB TTL timing or concurrency.
- [X] T025 [US3] Run `python -m pytest tests/integration` twice following `specs/001-api-endpoint-tests/quickstart.md` and record any repeatability failures for resolution.

**Checkpoint**: The documented workflow is repeatable and failures are actionable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T026 Reconcile all 17 rows in `specs/001-api-endpoint-tests/contracts/endpoint-coverage.md` with collected test identifiers and verify public and non-applicable cases are labeled.
- [X] T027 Run Ruff formatting and lint checks plus the full pytest suite described in `specs/001-api-endpoint-tests/quickstart.md`; fix only regressions introduced by this feature.
- [X] T028 Verify every acceptance criterion in `specs/001-api-endpoint-tests/spec.md`, document any uncovered behavior or contract discrepancies, and confirm no API contracts or ordinary user data were changed.

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (T001–T002) precedes foundational work (T003–T006).
- All stories depend on the shared fixtures from Phase 2.
- US1, US2, and US3 can be implemented independently after Phase 2; US1 first
  is the recommended MVP. US2's mapping update follows US1's mapping update to
  avoid concurrent edits to the same file.
- T025 follows creation of the scenarios it validates; final reconciliation
  and validation follow all story phases.

### Within Each User Story

- US1: T007–T012 can run concurrently in separate files; T013 follows them.
- US2: T014–T020 can run concurrently in separate files; T021 follows them
  and T013.
- US3: T022 and T024 touch separate files and can proceed independently;
  T023 follows test creation, and T025 follows T022–T024 and completed tests.
- All tasks marked `[P]` require the foundational fixtures to be complete and
  must not be run concurrently with another edit to the same file.

## Parallel Execution Examples

### User Story 1

- Run T008 for authentication success while T010 covers todos and T011 covers
  comments; each writes a separate test file.

### User Story 2

- Run T015 for authentication failures while T017 covers todo errors and
  T019 covers activity isolation; each writes a separate test file.

### User Story 3

- Work on T022's isolation verification and T024's documentation separately;
  finish T023 before T025's repeatability runs.

## Implementation Strategy

1. Complete setup and shared fixtures.
2. Deliver US1 as the MVP: all 17 endpoints have successful scenarios.
3. Add US2 negative and user-isolation coverage.
4. Complete US3 repeatability, documentation, and final verification.

No endpoint is added or changed by this feature, so a Postman collection update
is not required unless the scope changes.
