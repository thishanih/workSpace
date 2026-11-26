# Data Model: API Input Validation

## Request Input

A request input is a caller-supplied value associated with one of the API's existing operations.

| Attribute | Description |
|-----------|-------------|
| Operation | Existing HTTP method and route receiving the value |
| Source | Request body, path, query, or authentication credential |
| Field | Contract-defined input name |
| Rule | Presence, type, format, length, range, or allowed-value constraint |

### Request Input Inventory

| Operation | Caller-supplied values and rules |
|-----------|----------------------------------|
| `POST /api/auth/register` | `email` must be a valid email address and is normalized to lowercase; `name` is trimmed and 1-100 characters; `password` is 8-128 characters |
| `POST /api/auth/login` | `email` must be a valid email address and is normalized to lowercase; `password` is 1-128 characters; invalid credentials retain the existing 401 response |
| `POST /api/auth/refresh` | `refresh_token` must be a non-empty string; an invalid token retains the existing 401 response |
| `GET /api/users/me` | Bearer access credential; existing authentication behavior applies |
| `PATCH /api/users/me` | Bearer access credential; `name` is trimmed and 1-100 characters |
| `GET /api/todos` | Bearer access credential; `page` is an integer >= 1, default 1; `page_size` is an integer from 1 to 100, default 20 |
| `POST /api/todos` | Bearer access credential; `title` is trimmed and 1-200 characters; `description` is optional, nullable, and at most 5,000 characters; `status` is `pending`, `in_progress`, or `completed`, default `pending` |
| `GET /api/todos/{todo_id}` | Bearer access credential; resource identifier follows current 404 lookup behavior |
| `PATCH /api/todos/{todo_id}` | Bearer access credential; identifier follows current 404 lookup behavior; at least one supported field is required; `title` is 1-200 characters and cannot be null; `description` is nullable and at most 5,000 characters; `status` uses the supported values and cannot be null |
| `DELETE /api/todos/{todo_id}` | Bearer access credential; resource identifier follows current 404 lookup behavior |
| `GET /api/todos/{todo_id}/comments` | Bearer access credential; parent identifier follows current 404 lookup behavior; `page` and `page_size` use the todo-list bounds and defaults |
| `POST /api/todos/{todo_id}/comments` | Bearer access credential; parent identifier follows current 404 lookup behavior; `body` is trimmed and 1-2,000 characters |
| `PATCH /api/todos/{todo_id}/comments/{comment_id}` | Bearer access credential; both identifiers follow current 404 lookup behavior; required `body` is trimmed and 1-2,000 characters |
| `DELETE /api/todos/{todo_id}/comments/{comment_id}` | Bearer access credential; both identifiers follow current 404 lookup behavior |
| `GET /api/activities` | Bearer access credential; `page` and `page_size` use the list bounds and defaults; optional `todo_id` filter follows current 404 behavior |
| `GET /api/activities/{activity_id}` | Bearer access credential; activity identifier follows current 404 lookup behavior |

`GET /api/health` has no caller-supplied request fields and is outside the validation inventory.

### Canonical Field Names

The following entity-field names are canonical references for implementation tasks. Constraints below describe the existing API contract; they do not authorize a behavior change.

| Entity.field | Source | Constraint |
|--------------|--------|------------|
| `AuthRegisterInput.email` | `POST /api/auth/register` body | Valid email address; normalized to lowercase |
| `AuthRegisterInput.name` | `POST /api/auth/register` body | Trimmed string, 1-100 characters |
| `AuthRegisterInput.password` | `POST /api/auth/register` body | String, 8-128 characters |
| `AuthLoginInput.email` | `POST /api/auth/login` body | Valid email address; normalized to lowercase |
| `AuthLoginInput.password` | `POST /api/auth/login` body | String, 1-128 characters |
| `AuthRefreshInput.refresh_token` | `POST /api/auth/refresh` body | Non-empty string |
| `UserUpdateInput.name` | `PATCH /api/users/me` body | Trimmed string, 1-100 characters |
| `TodoCreateInput.title` | `POST /api/todos` body | Trimmed string, 1-200 characters |
| `TodoCreateInput.description` | `POST /api/todos` body | Optional and nullable; at most 5,000 characters |
| `TodoCreateInput.status` | `POST /api/todos` body | `pending`, `in_progress`, or `completed`; defaults to `pending` |
| `TodoUpdateInput.title` | `PATCH /api/todos/{todo_id}` body | Optional, non-null string, 1-200 characters |
| `TodoUpdateInput.description` | `PATCH /api/todos/{todo_id}` body | Optional and nullable; at most 5,000 characters |
| `TodoUpdateInput.status` | `PATCH /api/todos/{todo_id}` body | Optional, non-null value from the supported status set |
| `CommentCreateInput.body` | `POST /api/todos/{todo_id}/comments` body | Trimmed string, 1-2,000 characters |
| `CommentUpdateInput.body` | `PATCH /api/todos/{todo_id}/comments/{comment_id}` body | Trimmed string, 1-2,000 characters |
| `PaginationInput.page` | Todo, comment, and activity list queries | Integer >= 1; defaults to 1 |
| `PaginationInput.page_size` | Todo, comment, and activity list queries | Integer from 1 to 100; defaults to 20 |
| `ActivityListInput.todo_id` | `GET /api/activities` query | Optional resource filter; malformed or absent resources retain current 404 behavior |
| `ValidationIssue.loc` | Validation error response | Identifies the input location and field |
| `ValidationIssue.msg` | Validation error response | Concise correction-oriented message; must not repeat submitted values or secrets |
| `ValidationIssue.type` | Validation error response | Non-sensitive validation category |

### Compatibility-Only Inputs

These inputs already have established behavior and do not receive new field constraints in this feature. Their current status behavior is covered by the endpoint and authentication test suites.

| Input | Existing behavior |
|-------|-------------------|
| Authorization bearer credential | Protected operations retain existing authentication rules and 401 failures |
| Todo and nested-comment path identifiers | Malformed or absent resources retain current 404 behavior |
| Comment path identifier | Malformed or absent comments retain current 404 behavior |
| Activity path identifier | Malformed or absent activities retain current 404 behavior |

## Validation Issue

A validation issue is a client-safe description of a rejected request value.

| Attribute | Contract |
|-----------|----------|
| `loc` | Location segments identifying source and field, such as `["body", "email"]`, `["query", "page"]`, or `["path", "todo_id"]` |
| `msg` | Concise reason for rejection; must not echo the submitted value |
| `type` | Validation category as provided by the API's validation layer |

The public issue contains no raw `input`, validation `ctx`, documentation `url`, request body, or internal stack information.

## Validation Outcome

| Input state | Outcome |
|-------------|---------|
| Values satisfy the existing request contract | Existing endpoint processing, response, and effects are preserved |
| A body, path, or query field fails request validation | HTTP 422 with one or more sanitized validation issues; no data-changing operation occurs |
| Authentication fails | Existing HTTP 401 behavior is preserved |
| A resource identifier is malformed or refers to no resource | Existing HTTP 404 behavior is preserved |
| An application/domain error occurs | Existing status and `{"detail": "..."}` response behavior is preserved |

Unknown body fields remain ignored for compatibility with the current request-model behavior.
