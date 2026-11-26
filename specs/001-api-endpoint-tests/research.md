# Research: API Endpoint Test Coverage

## Test harness

**Decision**: Extend the existing pytest, FastAPI TestClient, and mongomock
integration tests instead of introducing a new testing framework.

**Rationale**: `tests/integration/test_api.py` already overrides the database
dependency, supplies an isolated mock database and test secret, and exercises
authentication and resource flows. The existing seven integration tests passed
on 2026-11-26.

**Alternatives considered**: Running against a live shared database is less
isolated; introducing another HTTP or test framework duplicates existing tools.

## Isolation and indexes

**Decision**: Use a new mock database per test, initialize applicable indexes,
and restore dependency overrides and settings on teardown. Keep test secrets and
data confined to tests. Prevent rate limiter state from leaking between cases
without weakening tests that explicitly cover rate limiting.

**Rationale**: The current fixture replaces the database dependency and thus
bypasses normal index initialization. Authentication and API rate counters are
process-local. A mock cannot establish real MongoDB TTL timing, concurrency, or
all index semantics; do not claim those behaviors are verified by the mock.

**Alternatives considered**: Reusing a shared mock risks test coupling; real
database integration is useful for engine-specific behavior but is not a
prerequisite for the scoped endpoint suite.

## Scenario design

**Decision**: Use named, independently identifiable scenarios with parameterized
negative cases, and maintain an explicit endpoint-to-test mapping.

**Rationale**: Success-only tests miss authentication, ownership, validation,
and data side effects. An explicit mapping makes the requested 17-endpoint
coverage auditable even though line coverage alone cannot prove it.

**Alternatives considered**: One large end-to-end test has poorer failure
localization; line-coverage percentages do not establish endpoint coverage.

## Expired tokens

**Decision**: Construct deliberately expired signed tokens using test-only
controlled timestamps and the existing test secret; never wait for expiry.

**Rationale**: Tests should be deterministic and fast while exercising the
real token-validation path. Separate wrong-purpose and token-reuse scenarios.

**Alternatives considered**: Sleeping until tokens expire is slow and flaky;
mocking validation would not test the actual authentication path.
