# Quickstart: API Endpoint Coverage

## Prerequisites

- Python and an activated project virtual environment with the existing
  runtime and development dependencies installed (`requirements.txt` and
  `requirements-dev.txt`).
- Run from the repository root. Tests must use an isolated mock database, not
  a development or production MongoDB database.

## Run and validate

After implementation, run the focused endpoint suite twice:

```bash
python -m pytest tests/integration
python -m pytest tests/integration
```

Both runs must pass without manual cleanup. Review
[endpoint-coverage.md](contracts/endpoint-coverage.md) to confirm every
inventoried endpoint maps to a successful test and its applicable negative,
authentication, and ownership tests.

Run formatting, lint, and the existing full suite:

```bash
python -m ruff format --check .
python -m ruff check .
python -m pytest
```

A failure must identify the scenario and expected versus actual outcome. Confirm
that test data and dependency overrides are cleaned up and ordinary user data is
untouched. See [data-model.md](data-model.md) for test data and boundaries.
