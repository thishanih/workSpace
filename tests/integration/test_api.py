from collections.abc import Iterator

import mongomock
import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import settings
from app.core.database import get_database
from app.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    mongo_client = mongomock.MongoClient()
    database = mongo_client["todo_api_test"]
    app.dependency_overrides[get_database] = lambda: database
    monkeypatch.setattr(
        settings,
        "jwt_secret_key",
        SecretStr("test-secret-key-with-at-least-32-characters"),
    )
    monkeypatch.setattr(settings, "auth_rate_limit_requests", 100)

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        mongo_client.close()


def _register(client: TestClient, email: str) -> tuple[str, str]:
    response = client.post(
        "/api/auth/register",
        json={"email": email, "name": "Test User", "password": "valid-password"},
    )
    assert response.status_code == 201
    payload = response.json()
    return payload["access_token"], payload["user"]["id"]


def test_todo_comment_and_activity_flow(client: TestClient) -> None:
    token, user_id = _register(client, "test@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    login = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "valid-password"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["id"] == user_id

    profile = client.get("/api/users/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["id"] == user_id
    assert "password_hash" not in profile.json()

    created = client.post(
        "/api/todos",
        headers=headers,
        json={
            "title": "Write tests",
            "description": "Exercise the API",
            "status": "pending",
        },
    )
    assert created.status_code == 201
    todo = created.json()
    assert todo["status"] == "pending"

    updated = client.patch(
        f"/api/todos/{todo['id']}",
        headers=headers,
        json={"status": "completed"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "completed"
    null_title = client.patch(
        f"/api/todos/{todo['id']}",
        headers=headers,
        json={"title": None},
    )
    assert null_title.status_code == 422

    comment_response = client.post(
        f"/api/todos/{todo['id']}/comments",
        headers=headers,
        json={"body": "Finished"},
    )
    assert comment_response.status_code == 201
    comment = comment_response.json()

    comments = client.get(
        f"/api/todos/{todo['id']}/comments",
        headers=headers,
    )
    assert comments.status_code == 200
    assert comments.json()["total"] == 1

    activities = client.get("/api/activities", headers=headers)
    assert activities.status_code == 200
    assert activities.json()["total"] == 3

    deleted_comment = client.delete(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers=headers,
    )
    assert deleted_comment.status_code == 204

    deleted_todo = client.delete(f"/api/todos/{todo['id']}", headers=headers)
    assert deleted_todo.status_code == 204

    final_activities = client.get("/api/activities", headers=headers)
    assert final_activities.status_code == 200
    assert final_activities.json()["total"] == 5


def test_users_cannot_access_another_users_todos(client: TestClient) -> None:
    owner_token, _ = _register(client, "owner@example.com")
    other_token, _ = _register(client, "other@example.com")

    created = client.post(
        "/api/todos",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"title": "Private todo"},
    )
    assert created.status_code == 201

    response = client.get(
        f"/api/todos/{created.json()['id']}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert response.status_code == 404


def test_registration_rejects_duplicate_email(client: TestClient) -> None:
    _register(client, "duplicate@example.com")
    duplicate = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "name": "Second User",
            "password": "valid-password",
        },
    )
    assert duplicate.status_code == 409


def test_refresh_rotates_tokens_and_rejects_reuse(client: TestClient) -> None:
    _register(client, "refresh@example.com")
    login = client.post(
        "/api/auth/login",
        json={"email": "refresh@example.com", "password": "valid-password"},
    )
    assert login.status_code == 200
    initial_tokens = login.json()
    assert initial_tokens["refresh_token"]

    refreshed = client.post(
        "/api/auth/refresh",
        json={"refresh_token": initial_tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    refreshed_tokens = refreshed.json()
    assert refreshed_tokens["access_token"] != initial_tokens["access_token"]
    assert refreshed_tokens["refresh_token"] != initial_tokens["refresh_token"]

    reused = client.post(
        "/api/auth/refresh",
        json={"refresh_token": initial_tokens["refresh_token"]},
    )
    assert reused.status_code == 401

    refresh_as_access = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {refreshed_tokens['refresh_token']}"},
    )
    assert refresh_as_access.status_code == 401

    profile = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {refreshed_tokens['access_token']}"},
    )
    assert profile.status_code == 200


def test_refresh_rejects_invalid_token(client: TestClient) -> None:
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not-a-valid-token"},
    )

    assert response.status_code == 401
