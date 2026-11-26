from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        pytest.param("GET", "/api/users/me", None, id="GET-users-me"),
        pytest.param(
            "PATCH", "/api/users/me", {"name": "Changed"}, id="PATCH-users-me"
        ),
        pytest.param("GET", "/api/todos", None, id="GET-todos"),
        pytest.param("POST", "/api/todos", {"title": "Blocked"}, id="POST-todos"),
        pytest.param("GET", "/api/todos/{todo_id}", None, id="GET-todo"),
        pytest.param(
            "PATCH",
            "/api/todos/{todo_id}",
            {"title": "Blocked"},
            id="PATCH-todo",
        ),
        pytest.param("DELETE", "/api/todos/{todo_id}", None, id="DELETE-todo"),
        pytest.param("GET", "/api/todos/{todo_id}/comments", None, id="GET-comments"),
        pytest.param(
            "POST",
            "/api/todos/{todo_id}/comments",
            {"body": "Blocked"},
            id="POST-comment",
        ),
        pytest.param(
            "PATCH",
            "/api/todos/{todo_id}/comments/{comment_id}",
            {"body": "Blocked"},
            id="PATCH-comment",
        ),
        pytest.param(
            "DELETE",
            "/api/todos/{todo_id}/comments/{comment_id}",
            None,
            id="DELETE-comment",
        ),
        pytest.param("GET", "/api/activities", None, id="GET-activities"),
        pytest.param(
            "GET",
            "/api/activities/{activity_id}",
            None,
            id="GET-activity",
        ),
    ],
)
@pytest.mark.parametrize(
    "authorization",
    [
        pytest.param(None, id="missing-bearer"),
        pytest.param("Bearer invalid", id="invalid-bearer"),
    ],
)
def test_protected_endpoint_rejects_missing_or_invalid_credentials(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
    database,
    method: str,
    path: str,
    body: dict[str, Any] | None,
    authorization: str | None,
) -> None:
    account = register_user("auth-matrix@example.com")
    token = account["access_token"]
    todo = create_todo(token)
    comment = create_comment(token, todo["id"])
    activity = client.get(
        "/api/activities",
        headers={"Authorization": f"Bearer {token}"},
    ).json()["items"][0]
    path = (
        path.replace("{todo_id}", todo["id"])
        .replace("{comment_id}", comment["id"])
        .replace("{activity_id}", activity["id"])
    )
    headers = {"Authorization": authorization} if authorization else {}
    before = {
        collection: database[collection].count_documents({})
        for collection in ("users", "todos", "comments", "activities", "refresh_tokens")
    }

    response = client.request(method, path, headers=headers, json=body)

    assert response.status_code == 401, response.text
    after = {
        collection: database[collection].count_documents({}) for collection in before
    }
    assert after == before


@pytest.mark.parametrize(
    "token_use",
    ["refresh", "access"],
    ids=["refresh-token-is-not-access-token", "valid-access-token"],
)
def test_protected_endpoint_requires_valid_access_token(
    client: TestClient,
    register_user,
    token_use: str,
) -> None:
    account = register_user("token-purpose@example.com")
    if token_use == "access":
        token = account["access_token"]
    else:
        token = account["refresh_token"]

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    expected_status = 200 if token_use == "access" else 401
    assert response.status_code == expected_status, response.text


def test_protected_endpoint_rejects_expired_access_token(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("expired-access@example.com")
    expired_token = jwt.encode(
        {
            "sub": account["user"]["id"],
            "exp": 1,
            "token_use": "access",
            "jti": "expired-access-token",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401, response.text
