# Todo API

A FastAPI todo API with MongoDB persistence, JWT authentication, todos, comments,
and activity history.

## Project structure

```text
todo-api/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   └── exceptions.py
│   ├── middleware/
│   │   ├── auth.py
│   │   ├── rate_limit.py
│   │   └── error_handler.py
│   ├── dependencies/
│   │   ├── auth.py
│   │   └── database.py
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── health/
│   │   │   └── router.py
│   │   ├── users/
│   │   │   ├── router.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── todos/
│   │   │   ├── router.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   ├── comments/
│   │   │   ├── router.py
│   │   │   ├── controller.py
│   │   │   ├── service.py
│   │   │   ├── schemas.py
│   │   │   └── models.py
│   │   └── activities/
│   │       ├── router.py
│   │       ├── controller.py
│   │       ├── service.py
│   │       ├── schemas.py
│   │       └── models.py
│   ├── utils/
│   │   ├── ids.py
│   │   ├── response.py
│   │   └── pagination.py
│   ├── routers/
│   │   └── api.py
│   └── main.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Run locally

Create and activate a virtual environment, then install the development
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Run MongoDB locally, then configure the app:

```bash
cp .env.example .env
```

Set `JWT_SECRET_KEY` in `.env` to a private random value with at least 32
characters. Install dependencies and start the development server:

```bash
uvicorn app.main:app --reload
```

The health endpoint is available at `http://127.0.0.1:8000/api/health`. Interactive
API docs are available at `http://127.0.0.1:8000/docs`.

## API endpoints

All endpoints are under `/api`. Except for health, registration, and login,
requests require `Authorization: Bearer <access_token>`.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `POST` | `/auth/register` | Register and receive an access token |
| `POST` | `/auth/login` | Sign in and receive an access token |
| `GET` | `/users/me` | Read the current user profile |
| `PATCH` | `/users/me` | Update the current user's name |
| `GET` | `/todos` | List the current user's todos |
| `POST` | `/todos` | Create a todo |
| `GET` | `/todos/{todo_id}` | Read a todo |
| `PATCH` | `/todos/{todo_id}` | Update a todo |
| `DELETE` | `/todos/{todo_id}` | Delete a todo and its comments |
| `GET` | `/todos/{todo_id}/comments` | List comments |
| `POST` | `/todos/{todo_id}/comments` | Add a comment |
| `PATCH` | `/todos/{todo_id}/comments/{comment_id}` | Update a comment |
| `DELETE` | `/todos/{todo_id}/comments/{comment_id}` | Delete a comment |
| `GET` | `/activities` | List the current user's activity history |
| `GET` | `/activities/{activity_id}` | Read an activity |

Todo status values are `pending`, `in_progress`, and `completed`. List endpoints
accept `page` and `page_size` query parameters. Data access is scoped to the
authenticated user. The built-in rate limiter is process-local; use a shared
rate-limiting store if deploying multiple workers.

Import `postman/todo-api.postman_collection.json` into Postman to try the
endpoints. Run **Auth → Register** first; it saves the access token used by
protected requests.

## Run integration tests

```bash
python -m pytest
```

## Checks before committing

Install the Git hook once after installing the development dependencies:

```bash
python -m pre_commit install
```

Before each commit, the hook formats and lints changed Python files with Ruff,
then runs the test suite. Keep the virtual environment activated when committing
so the hooks use the project's installed dependencies. Formatting and autofixable
lint issues are corrected automatically; the commit is blocked if any checks
still fail. To run all checks manually:

```bash
python -m pre_commit run --all-files
```
