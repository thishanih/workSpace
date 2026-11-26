from fastapi.testclient import TestClient


def test_todo_can_be_created_listed_read_updated_and_deleted(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("todos@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    payload = {
        "title": "Plan endpoint tests",
        "description": "Cover all todo operations",
        "status": "pending",
    }

    created = client.post("/api/todos", headers=headers, json=payload)
    assert created.status_code == 201, created.text
    todo = created.json()
    assert todo["title"] == payload["title"]
    assert todo["description"] == payload["description"]
    assert todo["status"] == "pending"
    assert todo["id"]

    listed = client.get("/api/todos", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == todo["id"]

    read = client.get(f"/api/todos/{todo['id']}", headers=headers)
    assert read.status_code == 200, read.text
    assert read.json()["id"] == todo["id"]

    updated = client.patch(
        f"/api/todos/{todo['id']}",
        headers=headers,
        json={"title": "Verify endpoint tests", "status": "completed"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["title"] == "Verify endpoint tests"
    assert updated.json()["status"] == "completed"
    assert client.get(f"/api/todos/{todo['id']}", headers=headers).json()["status"] == (
        "completed"
    )

    deleted = client.delete(f"/api/todos/{todo['id']}", headers=headers)
    assert deleted.status_code == 204
    assert client.get(f"/api/todos/{todo['id']}", headers=headers).status_code == 404
