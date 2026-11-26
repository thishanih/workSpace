from collections.abc import Callable, Iterator
from datetime import datetime, timezone
from typing import Any

import mongomock
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pymongo.database import Database

from app.core.config import settings
from app.core.database import get_database, initialize_indexes
from app.main import app
from app.middleware.rate_limit import RateLimitMiddleware

TEST_SECRET = "test-secret-key-with-at-least-32-characters"


def _rate_limit_middleware() -> RateLimitMiddleware | None:
    layer = app.middleware_stack
    while layer is not None:
        if isinstance(layer, RateLimitMiddleware):
            return layer
        layer = getattr(layer, "app", None)
    return None


def _mongomock_utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@pytest.fixture(autouse=True)
def verify_test_fixture_cleanup() -> Iterator[None]:
    previous_overrides = app.dependency_overrides.copy()
    previous_secret = settings.jwt_secret_key

    yield

    assert app.dependency_overrides == previous_overrides
    assert settings.jwt_secret_key == previous_secret
    rate_limiter = _rate_limit_middleware()
    if rate_limiter is not None:
        assert not rate_limiter._requests


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    mongo_client = mongomock.MongoClient()
    database = mongo_client["todo_api_test"]
    previous_overrides = app.dependency_overrides.copy()
    previous_secret = settings.jwt_secret_key
    app.dependency_overrides[get_database] = lambda: database
    initialize_indexes(database)
    monkeypatch.setattr(mongomock, "utcnow", _mongomock_utcnow)
    monkeypatch.setattr(settings, "jwt_secret_key", SecretStr(TEST_SECRET))

    try:
        with TestClient(app) as test_client:
            rate_limiter = _rate_limit_middleware()
            if rate_limiter is not None:
                rate_limiter._requests.clear()
            yield test_client
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)
        rate_limiter = _rate_limit_middleware()
        if rate_limiter is not None:
            rate_limiter._requests.clear()
        monkeypatch.setattr(settings, "jwt_secret_key", previous_secret)
        mongo_client.close()


@pytest.fixture
def register_user(
    client: TestClient,
) -> Callable[..., dict[str, Any]]:
    def register(
        email: str,
        *,
        name: str = "Test User",
        password: str = "valid-password",
    ) -> dict[str, Any]:
        response = client.post(
            "/api/auth/register",
            json={"email": email, "name": name, "password": password},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return register


@pytest.fixture
def create_todo(
    client: TestClient,
) -> Callable[..., dict[str, Any]]:
    def create(
        token: str,
        *,
        title: str = "Write tests",
        description: str | None = "Exercise the API",
        status: str = "pending",
    ) -> dict[str, Any]:
        response = client.post(
            "/api/todos",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": title,
                "description": description,
                "status": status,
            },
        )
        assert response.status_code == 201, response.text
        return response.json()

    return create


@pytest.fixture
def create_comment(
    client: TestClient,
) -> Callable[..., dict[str, Any]]:
    def create(token: str, todo_id: str, body: str = "Finished") -> dict[str, Any]:
        response = client.post(
            f"/api/todos/{todo_id}/comments",
            headers={"Authorization": f"Bearer {token}"},
            json={"body": body},
        )
        assert response.status_code == 201, response.text
        return response.json()

    return create


@pytest.fixture
def database(client: TestClient) -> Database:
    return app.dependency_overrides[get_database]()
