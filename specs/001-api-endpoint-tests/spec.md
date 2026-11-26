# Feature Specification: API Endpoint Test Coverage

**Feature Branch**: `feature/api-endpoint-tests`

**Created**: 2026-11-26

**Status**: Draft

**Input**: User description: "test case create using whole api endpoint including"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify every existing endpoint (Priority: P1)

As a maintainer, I want automated checks for every existing application endpoint
so that a change cannot silently break a supported user action.

**Why this priority**: Basic coverage of every existing endpoint is the core
request and provides a baseline for safe changes.

**Independent Test**: Run the endpoint tests and inspect the coverage mapping to
confirm that every endpoint in the inventory has a successful behavior check.

**Acceptance Scenarios**:

1. **Given** a working service and valid inputs, **When** each listed endpoint
   is exercised, **Then** its expected successful response and relevant data
   changes are verified.
2. **Given** an endpoint's expected behavior changes, **When** a test observes
   an unexpected response or data state, **Then** the test fails and identifies
   the affected endpoint and scenario.

### User Story 2 - Verify invalid and unauthorized requests (Priority: P2)

As a maintainer, I want checks for invalid input, missing or invalid credentials,
and cross-user access so that errors and private data remain protected.

**Why this priority**: Successful requests alone do not demonstrate validation
or isolation between users.

**Independent Test**: Run negative and authorization scenarios separately and
confirm their expected errors and unchanged protected data.

**Acceptance Scenarios**:

1. **Given** a protected action, **When** a request has missing or invalid
   credentials, **Then** access is denied and no protected data is changed.
2. **Given** a resource owned by another user, **When** it is read, changed, or
   deleted by a different user, **Then** access is denied without exposing or
   modifying that resource.
3. **Given** a request with invalid fields, identifiers, or pagination values,
   **When** it is submitted, **Then** the documented validation or not-found
   behavior is verified.

### User Story 3 - Make results repeatable and understandable (Priority: P3)

As a contributor, I want isolated, repeatable test cases and clear instructions
so I can run the checks and diagnose failures before submitting changes.

**Why this priority**: Reliable and accessible checks are necessary for the
coverage to remain useful over time.

**Independent Test**: Follow the documented test instructions twice against
an isolated test environment and confirm both runs complete with consistent
results without modifying ordinary user data.

**Acceptance Scenarios**:

1. **Given** the documented prerequisites are met, **When** a contributor runs
   the suite twice, **Then** both runs report results without depending on data
   left by the previous run.
2. **Given** a failed scenario, **When** a contributor reviews the results,
   **Then** the endpoint, scenario, and expected versus actual outcome are
   identifiable.

### Edge Cases

- Empty, malformed, missing, and boundary-value inputs where applicable.
- Missing, invalid, expired, wrong-purpose, or already-used credentials.
- Invalid, missing, deleted, or other users' resource identifiers.
- Empty results and pagination boundaries.
- A deleted todo and its related comments; activity history after changes.
- Repeated runs, independent test data, and unavailable test dependencies.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The test suite MUST cover each of the 17 existing application
  endpoints in the inventory below with at least one successful scenario that
  verifies the response and any relevant state change.
- **FR-002**: The suite MUST verify registration and login success and
  rejection, and refresh token rotation, invalid token rejection, and reuse
  rejection.
- **FR-003**: The suite MUST verify profile reading and updating, including
  rejected invalid updates.
- **FR-004**: The suite MUST verify todo creation, listing, reading, updating,
  and deletion, including applicable status and pagination boundaries.
- **FR-005**: The suite MUST verify comment creation, listing, updating, and
  deletion, including deletion of associated comments when a todo is deleted.
- **FR-006**: The suite MUST verify activity listing and retrieval for relevant
  user actions and verify that another user's activities are not exposed.
- **FR-007**: For each protected endpoint, the suite MUST verify missing and
  invalid credentials are rejected. For resource-specific actions, it MUST
  also verify missing or invalid identifiers and cross-user access as applicable.
- **FR-008**: For endpoints accepting input, the suite MUST exercise relevant
  invalid and boundary inputs and verify expected error behavior without
  unintended state changes.
- **FR-009**: The suite MUST isolate its test data from ordinary user data and
  produce consistent results across repeated runs.
- **FR-010**: Test results MUST identify the failed endpoint and scenario.
  Documentation MUST explain prerequisites, execution, and any required test
  data setup or cleanup.
- **FR-011**: A coverage mapping MUST associate every endpoint in the inventory
  with its successful test and applicable negative, authentication, and
  ownership scenarios, identifying any scenarios that do not apply.
- **FR-012**: The feature MUST preserve existing endpoint behavior; changes to
  the endpoint contracts are outside its scope.

**Endpoint inventory** (all paths are under `/api`):

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/auth/register` | Register |
| POST | `/auth/login` | Sign in |
| POST | `/auth/refresh` | Rotate tokens |
| GET | `/users/me` | Read profile |
| PATCH | `/users/me` | Update profile |
| GET | `/todos` | List todos |
| POST | `/todos` | Create a todo |
| GET | `/todos/{todo_id}` | Read a todo |
| PATCH | `/todos/{todo_id}` | Update a todo |
| DELETE | `/todos/{todo_id}` | Delete a todo |
| GET | `/todos/{todo_id}/comments` | List comments |
| POST | `/todos/{todo_id}/comments` | Create a comment |
| PATCH | `/todos/{todo_id}/comments/{comment_id}` | Update a comment |
| DELETE | `/todos/{todo_id}/comments/{comment_id}` | Delete a comment |
| GET | `/activities` | List activities |
| GET | `/activities/{activity_id}` | Read an activity |

### Key Entities

- **Endpoint scenario**: An endpoint, input and user context, expected response,
  and expected state or isolation outcome.
- **Test user and resources**: Isolated accounts, todos, comments, and
  activities used to verify user journeys and ownership.
- **Coverage mapping**: The relationship between each endpoint and its
  successful and applicable negative scenarios.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 17 inventoried endpoints have a passing successful scenario
  and an entry in the coverage mapping.
- **SC-002**: All protected endpoints have passing missing-credential and
  invalid-credential scenarios; all applicable resource-specific actions have
  passing cross-user isolation scenarios.
- **SC-003**: Two consecutive runs in a prepared test environment pass without
  manual cleanup between runs or changes to ordinary user data.
- **SC-004**: A reviewer can identify the affected endpoint and expected
  outcome for every failed scenario from its reported result.

## Assumptions

- The scope is the 17 application endpoints currently documented in the
  repository, not generated documentation routes or future endpoints.
- Existing automated tests may be reused and extended rather than duplicated.
- Existing behavior is the reference unless documentation and implementation
  disagree; discrepancies should be surfaced rather than silently changed.
- A dedicated test environment and test data are available. This feature does
  not introduce load, performance, or external security certification tests.
- No endpoint is added or changed, so the existing Postman collection need not
  be changed solely for this feature.
