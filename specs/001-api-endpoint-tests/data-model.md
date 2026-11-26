# Test Data Model: API Endpoint Coverage

This feature adds no production entities or schema migrations. These are
test-data concepts and their relationships.

## Test account

- Fields: unique email, valid name and password, user ID, access token, refresh token.
- Relationships: owns todos and activities; authors comments on owned todos.
- Validation: registration names are 1–100 characters, passwords 8–128, and
  email must be valid; profile name updates are 1–100 characters.
- Isolation: create separate owner and other-user accounts for ownership tests.

## Todo

- Fields: ID, owner, title, optional description, status, timestamps.
- Validation: title is 1–200 characters, description at most 5,000 characters,
  status is `pending`, `in_progress`, or `completed`; update must not be empty.
- Relationships: belongs to one owner and may have comments and activities.
- Transitions: create, read/list, update, delete; deletion removes comments.

## Comment

- Fields: ID, todo ID, author ID, body, timestamps.
- Validation: body is 1–2,000 characters; todo and comment must be accessible
  to the current user.
- Transitions: create, list, update, delete; removed when its todo is deleted.

## Activity

- Fields: ID, owner, action, entity reference, optional todo reference, summary,
  and creation time.
- Relationships: belongs to an owner and records relevant resource actions.
- Validation: list and read expose only the current user's records.

## Token and scenario state

- Access token: authenticates protected requests; reject invalid, expired,
  missing, and refresh-purpose credentials.
- Refresh token: belongs to a user and has an ID and expiry; successful refresh
  consumes it and issues a new pair; reuse must fail.
- Scenario: method, path, input, actor, expected response, expected state, and
  test identifier.
- **Scenario.page**: List page number, at least 1.
- **Scenario.page_size**: List page size, from 1 through 100.
