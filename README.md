# Todo API

A minimal FastAPI project containing only a health endpoint.

## Run locally

From the `todo-api` directory, install dependencies and start the development server:

```bash
python3 -m pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/api/health`.

## Run integration tests

```bash
python3 -m pytest
```

## Checks before committing

Install the Git hook once after installing the development dependencies:

```bash
python3 -m pre_commit install
```

Before each commit, the hook formats and lints changed Python files with Ruff,
then runs the test suite. Formatting and autofixable lint issues are corrected
automatically; the commit is blocked if any checks still fail. To run all checks
manually:

```bash
python3 -m pre_commit run --all-files
```
