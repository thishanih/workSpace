# Research: API Input Validation

## Decision 1: Keep validation in the existing Python API stack

**Decision**: Use FastAPI request validation and the repository's Pydantic v2 request models. Add a small shared validation module for repeated rules instead of adding a new validation framework or migrating the service.

**Rationale**: The API already declares body constraints with Pydantic `BaseModel`, `Field`, `field_validator`, and `model_validator`, and query constraints with FastAPI `Query`. Reusing those patterns keeps validation close to each endpoint contract while allowing common rules to be shared. The user's Node.js/Zod reference is treated as an example of a reusable validation approach, not as a request to change this Python service's runtime.

**Alternatives considered**:

- Introduce a new validation dependency: rejected because the current stack already provides the necessary validation features.
- Migrate the service to Node.js/Zod: rejected because it would replace the existing service platform and is outside the feature's validation scope.
- Put all field rules in one global schema: rejected because endpoint-specific request models already express the distinct rules and should remain the source of truth.

## Decision 2: Sanitize validation responses while retaining the 422 contract

**Decision**: Handle FastAPI `RequestValidationError` in the existing exception-handler registration. Return status 422 with a top-level `detail` array containing only each issue's `loc`, `msg`, and `type`. Do not return submitted `input`, validation `ctx`, documentation `url`, or the request body.

**Rationale**: FastAPI's default validation response includes structured field details but may also include the submitted value. Passwords, refresh tokens, and other caller data must not be echoed. Keeping the status and top-level `detail` key retains the existing HTTP validation convention while filtering the response to a stable, client-useful subset. The repository's current tests assert 422 for invalid request models and pagination values; they do not depend on the raw input field.

**Alternatives considered**:

- Keep FastAPI's default response: rejected because the default error details can include the submitted value.
- Return a plain-text response or a new top-level error shape: rejected because it unnecessarily changes the API's JSON convention.
- Change validation errors to 400: rejected because existing behavior and tests use 422.

## Decision 3: Preserve existing non-schema error behavior

**Decision**: Do not change authentication, domain, or resource lookup semantics as part of this feature. Invalid or absent resource identifiers continue to follow the current 404 behavior; authentication failures remain 401. Unknown request-body fields remain ignored as they are today.

**Rationale**: The feature targets consistent validation without changing business rules or successful API behavior. Existing integration tests explicitly expect 404 for both malformed and well-formed-but-absent resource IDs, and the request models currently use Pydantic's default extra-field handling. Changing these behaviors would be a separate API contract decision.

**Alternatives considered**:

- Convert malformed resource identifiers to 422: rejected because that changes an asserted 404 behavior and is not required to validate existing body and query constraints.
- Forbid all unknown body fields: rejected because existing clients may rely on the current ignore behavior and no requirement asks for a breaking change.

## Project Evidence

- Existing validation rules are defined in `app/modules/auth/schemas.py`, `app/modules/users/schemas.py`, `app/modules/todos/schemas.py`, and `app/modules/comments/schemas.py`.
- Pagination constraints are repeated in `app/modules/todos/router.py`, `app/modules/comments/router.py`, and `app/modules/activities/router.py`.
- `app/middleware/error_handler.py` registers `AppError` and database handlers; no request-validation handler is currently registered.
- `app/utils/ids.py` maps malformed resource identifiers to the existing 404 error behavior.
- `tests/integration/test_todo_errors.py`, `test_auth_errors.py`, `test_activity_errors.py`, and `test_pagination.py` exercise existing validation and error behavior.

## References

- FastAPI, Handling Errors: <https://fastapi.tiangolo.com/tutorial/handling-errors/>
- FastAPI, Query Parameters and String Validations: <https://fastapi.tiangolo.com/tutorial/query-params-str-validations/>
- FastAPI, Request Body: <https://fastapi.tiangolo.com/tutorial/body/>
- Pydantic, Validation Errors: <https://docs.pydantic.dev/latest/errors/errors/>
- Pydantic Core, `ValidationError.errors()` API: <https://docs.pydantic.dev/latest/api/pydantic_core/#pydantic_core.ValidationError.errors>
