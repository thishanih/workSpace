from fastapi.testclient import TestClient


def test_todo_comment_and_activity_flow(
    client: TestClient,
    register_user,
    create_comment,
) -> None:
    account = register_user("test@example.com")
    token = account["access_token"]
    user_id = account["user"]["id"]
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

    comment = create_comment(token, todo["id"])

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


def test_users_cannot_access_another_users_todos(
    client: TestClient,
    register_user,
) -> None:
    owner_token = register_user("owner@example.com")["access_token"]
    other_token = register_user("other@example.com")["access_token"]

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


def test_registration_rejects_duplicate_email(
    client: TestClient,
    register_user,
) -> None:
    register_user("duplicate@example.com")
    duplicate = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "name": "Second User",
            "password": "valid-password",
        },
    )
    assert duplicate.status_code == 409


def test_refresh_rotates_tokens_and_rejects_reuse(
    client: TestClient,
    register_user,
) -> None:
    register_user("refresh@example.com")
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
