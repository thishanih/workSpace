# Tasks: API Input Validation

**Input**: Design documents from `/specs/002-api-input-validation/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/request-validation.md`

**Tests**: Integration tests are required by SC-001 and SC-003 in `spec.md`.

**Organization**: Tasks are grouped by user story. This API has 16 input-bearing operations; `/api/health` is unchanged.

## Phase 1: Setup

**Purpose**: The FastAPI project, request schemas, integration-test structure, and Postman collection already exist. No project initialization is needed.

## Phase 2: Foundational

**Purpose**: Add shared validation infrastructure used by every story.

- [X] T001 [P] Register a `RequestValidationError` handler in `app/middleware/error_handler.py` that returns status 422 and only the sanitized `loc`, `msg`, and `type` fields defined by `ValidationIssue.loc`, `ValidationIssue.msg`, and `ValidationIssue.type` in `specs/002-api-input-validation/data-model.md`; never return `input`, `ctx`, `url`, or the request body.
- [X] T002 [P] Define reusable FastAPI query aliases for `PaginationInput.page` and `PaginationInput.page_size` as constrained in `specs/002-api-input-validation/data-model.md` in `app/utils/validation.py`.

**Checkpoint**: Shared 422 handling and reusable pagination constraints are available before endpoint-specific work.

## Phase 3: User Story 1 - Reject invalid requests safely (Priority: P1) 🎯 MVP

**Goal**: Reject invalid body, query, and applicable path inputs before an operation can change data, while retaining established 401/404 behavior.

**Independent Test**: Run `python -m pytest tests/integration/test_request_validation.py tests/integration/test_pagination.py`; invalid values return 422 or the established auth/resource error, and invalid create/update requests leave stored data unchanged.

### Tests for User Story 1

- [X] T003 [US1] Add integration coverage for invalid request bodies and query values across all applicable input-bearing operations, including required/optional fields, boundaries, filters, and no-mutation assertions for rejected writes, in `tests/integration/test_request_validation.py`.

### Implementation for User Story 1

- [X] T004 [P] [US1] Align authentication request schemas with `AuthRegisterInput.email`, `AuthRegisterInput.name`, `AuthRegisterInput.password`, `AuthLoginInput.email`, `AuthLoginInput.password`, and `AuthRefreshInput.refresh_token` from `specs/002-api-input-validation/data-model.md` in `app/modules/auth/schemas.py`.
- [X] T005 [P] [US1] Align the profile update schema with `UserUpdateInput.name` from `specs/002-api-input-validation/data-model.md` in `app/modules/users/schemas.py`.
- [X] T006 [P] [US1] Align todo create/update schemas with `TodoCreateInput.title`, `TodoCreateInput.description`, `TodoCreateInput.status`, `TodoUpdateInput.title`, `TodoUpdateInput.description`, and `TodoUpdateInput.status` from `specs/002-api-input-validation/data-model.md` in `app/modules/todos/schemas.py`.
- [X] T007 [P] [US1] Align comment create/update schemas with `CommentCreateInput.body` and `CommentUpdateInput.body` from `specs/002-api-input-validation/data-model.md` in `app/modules/comments/schemas.py`.
- [X] T008 [P] [US1] Use the shared pagination aliases in todo, comment, and activity list routes for `PaginationInput.page` and `PaginationInput.page_size`, and preserve the existing 404 behavior for `ActivityListInput.todo_id`, in `app/modules/todos/router.py`, `app/modules/comments/router.py`, and `app/modules/activities/router.py`.
- [X] T009 [US1] Update the invalid-body and invalid-query examples in `postman/todo-api.postman_collection.json` and verify the corresponding existing requests still target the correct method, URL, authentication, parameters, and body.

**Checkpoint**: Every covered invalid request is rejected before mutation; existing authentication and resource lookup behavior remains unchanged.

## Phase 4: User Story 2 - Preserve valid API use (Priority: P1)

**Goal**: Ensure requests that satisfy the established API contract retain their prior outcomes, including defaults and partial updates.

**Independent Test**: Run `python -m pytest tests/integration/test_request_validation_compatibility.py tests/integration/test_auth_endpoints.py tests/integration/test_todo_endpoints.py tests/integration/test_comment_endpoints.py tests/integration/test_user_endpoints.py tests/integration/test_activity_endpoints.py`; successful responses and effects match the existing API behavior.

### Tests for User Story 2

- [X] T010 [P] [US2] Add regression coverage for valid requests, omitted optional values, default pagination/status values, and partial updates in `tests/integration/test_request_validation_compatibility.py`.

### Implementation for User Story 2

- [X] T011 [US2] Update and verify the successful request examples for all affected operations in `postman/todo-api.postman_collection.json`, preserving each request's method, URL, authentication, parameters, and body.

**Checkpoint**: Existing successful endpoint flows remain compatible with the new validation rules.

## Phase 5: User Story 3 - Correct rejected input (Priority: P2)

**Goal**: Give clients safe, actionable details about invalid inputs without exposing submitted values or internal diagnostics.

**Independent Test**: Run `python -m pytest tests/integration/test_validation_error_contract.py`; assert the response identifies input locations and reasons without including values, secrets, request bodies, or internal diagnostics.

### Tests for User Story 3

- [X] T012 [P] [US3] Add integration tests for the public 422 issue shape, multiple invalid fields, sensitive values, and the absence of `input`, `ctx`, `url`, raw body, and stack details in `tests/integration/test_validation_error_contract.py`.

### Implementation for User Story 3

- [X] T013 [US3] Document the sanitized 422 response, its fields, and client correction guidance in `README.md` and `specs/002-api-input-validation/contracts/request-validation.md`.
- [X] T014 [US3] Add a representative sanitized 422 response example and verify its response fields in `postman/todo-api.postman_collection.json`.

**Checkpoint**: Clients can identify rejected fields and correct them without receiving submitted values or internal details.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the full implementation against the documented scenarios.

- [X] T015 Run the focused and full test commands in `specs/002-api-input-validation/quickstart.md` and resolve any failures across the affected `tests/integration/` suites.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No work is needed; the project structure already exists.
- **Foundational (Phase 2)**: T001 and T002 can run in parallel and must complete before user-story work.
- **User Story 1 (Phase 3)**: Depends on Phase 2. T003 adds the failing invalid-input cases before schema and route alignment. T004-T008 touch separate files and can run in parallel after T003; T009 verifies the updated collection after endpoint behavior is in place.
- **User Story 2 (Phase 4)**: Depends on User Story 1 so valid requests are tested against the completed validation changes. T010 and T011 touch separate files and can run in parallel.
- **User Story 3 (Phase 5)**: Depends on Phase 2 and User Story 1. T012-T014 touch separate files and can run in parallel.
- **Polish (Phase 6)**: Depends on all desired stories being complete.

### User Story Dependencies

- **US1 (P1)**: Depends only on foundational tasks; delivers the MVP.
- **US2 (P1)**: Depends on US1 so compatibility coverage includes the applied validation.
- **US3 (P2)**: Depends on US1 and foundational 422 handling so sanitized feedback is verified against real validation failures.

### Parallel Opportunities

- Run T001 with T002.
- In US1, run T004-T008 in parallel after T003; T009 follows endpoint implementation because it verifies behavior.
- In US2, run T010 and T011 in parallel after US1 is complete.
- In US3, run T012, T013, and T014 in parallel after US1 is complete.

## Parallel Examples

### User Story 1

```text
After T003:
Task: T004 Align authentication request schemas in app/modules/auth/schemas.py
Task: T005 Align profile update schema in app/modules/users/schemas.py
Task: T006 Align todo request schemas in app/modules/todos/schemas.py
Task: T007 Align comment request schemas in app/modules/comments/schemas.py
Task: T008 Apply shared query aliases in the todo, comment, and activity routers
```

### User Story 2

```text
After US1:
Task: T010 Add valid-request compatibility tests in tests/integration/test_request_validation_compatibility.py
Task: T011 Update successful requests in postman/todo-api.postman_collection.json
```

### User Story 3

```text
After US1:
Task: T012 Add sanitized-error integration tests in tests/integration/test_validation_error_contract.py
Task: T013 Document the 422 contract in README.md and specs/002-api-input-validation/contracts/request-validation.md
Task: T014 Add the sanitized error example in postman/todo-api.postman_collection.json
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete T001-T002 to make shared validation behavior available.
2. Complete T003-T009 to cover invalid input across existing endpoints.
3. Validate US1 independently with the command under its Independent Test.
4. Deliver the invalid-input rejection increment before adding broader compatibility and client-guidance work.

### Incremental Delivery

1. Foundation + US1: safely reject invalid inputs without mutating data.
2. US2: demonstrate valid request compatibility across the existing endpoint suite.
3. US3: document and verify actionable sanitized validation feedback.
4. Complete T015 for full regression validation.

## Notes

- Every task uses the required checkbox, sequential ID, applicable parallel/story labels, and at least one exact file path.
- Field constraints are cited from the canonical `Entity.field` definitions in `data-model.md`; task descriptions do not duplicate unchanged constraint values.
- Existing authentication failures and malformed/absent resource lookups retain their current 401/404 behavior.
