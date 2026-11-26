# Implementation Plan: API Input Validation

**Branch**: `feature/api-input-validation` | **Date**: 2026-11-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-api-input-validation/spec.md`

## Summary

Apply consistent validation across all existing input-bearing API operations while preserving successful request behavior. Reuse the current FastAPI and Pydantic request-validation patterns, add a focused shared validator module for common rules, and return sanitized validation errors that do not echo submitted values. Keep the existing authentication, resource-not-found, and domain-error behavior unchanged.

## Technical Context

**Language/Version**: Python; current workspace interpreter is 3.14.10. The repository does not declare a supported Python range.

**Primary Dependencies**: FastAPI, Pydantic v2 APIs, PyMongo, and pytest; versions are managed in `requirements.txt` without upper bounds.

**Storage**: MongoDB. Integration tests use an in-memory MongoDB mock.

**Testing**: `python -m pytest`; focused API integration tests live under `tests/integration/`.

**Target Platform**: ASGI web service run with Uvicorn. Deployment operating system is not specified.

**Project Type**: Python web service.

**Performance Goals**: No numeric latency target is defined. Validation must not add database work to rejected requests or change the existing valid-request flow.

**Constraints**: Preserve successful response status, body, and effects. Keep 422 for request-field validation, omit raw input from error responses, and preserve existing 401 authentication and 404 resource/error behavior.

**Scale/Scope**: All 16 existing operations that accept caller-supplied values across the 17 documented operations; `/api/health` has no request fields and is excluded.

## Constitution Check

The constitution file contains only template placeholders and no ratified principles or project-specific gates. No enforceable constitution rule is available to evaluate. The design follows the repository's existing FastAPI/Pydantic, middleware, and integration-test structure and adds no dependency or separate service.

**Gate**: Pass with note — no active constitution constraints found; retain this limitation for future constitution ratification.

## Project Structure

### Documentation (this feature)

```text
specs/002-api-input-validation/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── request-validation.md
```

### Source Code (repository root)

```text
app/
├── middleware/
│   └── error_handler.py
├── modules/
│   ├── auth/
│   │   ├── router.py
│   │   └── schemas.py
│   ├── users/
│   │   ├── router.py
│   │   └── schemas.py
│   ├── todos/
│   │   ├── router.py
│   │   └── schemas.py
│   ├── comments/
│   │   ├── router.py
│   │   └── schemas.py
│   └── activities/
│       └── router.py
└── utils/
    ├── ids.py
    └── validation.py

tests/
└── integration/
    └── test_request_validation.py

postman/
└── todo-api.postman_collection.json
```

**Structure Decision**: Keep endpoint-specific request models beside their existing module routers. Put only genuinely shared request rules in `app/utils/validation.py`; use the existing middleware registration point for sanitized request-validation errors. Extend the existing integration-test suite and Postman collection rather than introducing a new project or test framework.
