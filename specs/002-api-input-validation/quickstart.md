# Quickstart: Validate API Input Handling

This guide verifies request validation after implementation. The API's test suite uses isolated in-memory MongoDB mocks and does not require access to ordinary database data.

## Prerequisites

- Use the repository's configured Python environment.
- Install the project and development dependencies as described in the repository README.

## Focused Validation

Run the integration cases covering request validation, existing error behavior, and query bounds:

```bash
python -m pytest \
  tests/integration/test_request_validation.py \
  tests/integration/test_validation_error_contract.py \
  tests/integration/test_request_validation_compatibility.py \
  tests/integration/test_auth_errors.py \
  tests/integration/test_user_errors.py \
  tests/integration/test_todo_errors.py \
  tests/integration/test_comment_errors.py \
  tests/integration/test_activity_errors.py \
  tests/integration/test_pagination.py
```

Expected outcomes:

- Invalid body and query values return HTTP 422 with a `detail` array containing location, message, and type.
- Validation responses do not contain submitted values, raw request bodies, or internal diagnostics.
- Existing authentication failures remain HTTP 401; malformed or absent resource lookups remain HTTP 404.
- Invalid create/update requests leave stored records unchanged.
- Valid request scenarios retain their existing response and data behavior.

## Regression Validation

Run the full test suite:

```bash
python -m pytest
```

The repository recommends running the endpoint integration suite twice to verify repeatability:

```bash
python -m pytest tests/integration
python -m pytest tests/integration
```

## Postman Contract Check

Verify the saved requests in `postman/todo-api.postman_collection.json` still use the correct method, URL, authentication, parameters, and body. Run representative invalid requests and confirm their 422 response contains only sanitized issue details; confirm existing successful examples remain unchanged.
