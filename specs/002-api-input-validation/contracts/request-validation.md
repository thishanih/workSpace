# Request Validation Contract

All paths are prefixed with `/api`. This contract covers the 16 existing operations that accept caller-supplied values. `GET /api/health` has no request fields and remains unchanged.

## Endpoint Input Coverage

| Method and path | Request values covered |
|-----------------|------------------------|
| `POST /auth/register` | Body: `email`, `name`, `password` |
| `POST /auth/login` | Body: `email`, `password` |
| `POST /auth/refresh` | Body: `refresh_token` |
| `GET /users/me` | Authorization bearer credential |
| `PATCH /users/me` | Authorization bearer credential; body: `name` |
| `GET /todos` | Authorization bearer credential; query: `page`, `page_size` |
| `POST /todos` | Authorization bearer credential; body: `title`, `description`, `status` |
| `GET /todos/{todo_id}` | Authorization bearer credential; path: `todo_id` |
| `PATCH /todos/{todo_id}` | Authorization bearer credential; path: `todo_id`; body: `title`, `description`, `status` |
| `DELETE /todos/{todo_id}` | Authorization bearer credential; path: `todo_id` |
| `GET /todos/{todo_id}/comments` | Authorization bearer credential; path: `todo_id`; query: `page`, `page_size` |
| `POST /todos/{todo_id}/comments` | Authorization bearer credential; path: `todo_id`; body: `body` |
| `PATCH /todos/{todo_id}/comments/{comment_id}` | Authorization bearer credential; path: `todo_id`, `comment_id`; body: `body` |
| `DELETE /todos/{todo_id}/comments/{comment_id}` | Authorization bearer credential; path: `todo_id`, `comment_id` |
| `GET /activities` | Authorization bearer credential; query: `page`, `page_size`, optional `todo_id` |
| `GET /activities/{activity_id}` | Authorization bearer credential; path: `activity_id` |

The field constraints are defined in [data-model.md](../data-model.md). Registration, login, and refresh remain public routes; all other operations retain their existing bearer-authentication requirements.

## Request Validation Error

Invalid body or query values, and any path value rejected by request validation before resource lookup, return HTTP `422` and a JSON response with a top-level `detail` array. Each issue contains exactly `loc` (input location), `msg` (concise correction-oriented message), and `type` (validation category). Resource identifiers continue to follow the existing `404` lookup behavior.

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character"
    }
  ]
}
```

The response MUST NOT include submitted values (`input`), validation context (`ctx`), a documentation URL (`url`), the raw request body, or internal diagnostics. Error messages MUST NOT repeat secrets or the rejected value.

## Compatibility Rules

- Valid requests retain their current response status, response body, and data effects.
- Invalid data-changing requests do not create or mutate records.
- Invalid request fields retain HTTP `422`; malformed credentials retain existing HTTP `401` behavior.
- Malformed and absent resource identifiers retain existing HTTP `404` behavior.
- Existing application/domain errors retain their status and top-level `detail` string.
- Unknown body fields remain ignored, matching current request-model behavior.

## Verification Scope

Integration coverage exercises every input-bearing operation, includes invalid and valid boundary cases for body/query inputs, verifies the sanitized error shape, and verifies that rejected mutating requests leave stored data unchanged. The Postman collection retains each endpoint's method, URL, authentication, parameters, and body while documenting representative validation failures.
