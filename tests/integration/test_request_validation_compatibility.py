from fastapi.testclient import TestClient


def test_todo_defaults_and_partial_update_preserve_omitted_fields(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("validation-compatibility@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    created = client.post(
        "/api/todos",
        headers=headers,
        json={
            "title": "Original title",
            "description": "Keep this",
            "status": "in_progress",
        },
    )
    assert created.status_code == 201, created.text
    todo = created.json()

    updated = client.patch(
        f"/api/todos/{todo['id']}",
        headers=headers,
        json={"title": "Updated title"},
    )

    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Updated title"
    assert updated.json()["description"] == "Keep this"
    assert updated.json()["status"] == "in_progress"


def test_todo_create_defaults_remain_unchanged(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("validation-defaults@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    response = client.post(
        "/api/todos", headers=headers, json={"title": "Default values"}
    )

    assert response.status_code == 201, response.text
    assert response.json()["description"] is None
    assert response.json()["status"] == "pending"


def test_list_routes_keep_default_pagination(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
) -> None:
    account = register_user("validation-pagination-defaults@example.com")
    token = account["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    todo = create_todo(token)
    create_comment(token, todo["id"])

    responses = [
        client.get("/api/todos", headers=headers),
        client.get(f"/api/todos/{todo['id']}/comments", headers=headers),
        client.get("/api/activities", headers=headers),
    ]

    assert all(response.status_code == 200 for response in responses)
    assert all(response.json()["page"] == 1 for response in responses)
    assert all(response.json()["page_size"] == 20 for response in responses)
