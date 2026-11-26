from fastapi.testclient import TestClient


def test_comment_can_be_created_listed_updated_and_deleted(
    client: TestClient,
    register_user,
    create_todo,
) -> None:
    account = register_user("comments@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    todo = create_todo(account["access_token"])

    created = client.post(
        f"/api/todos/{todo['id']}/comments",
        headers=headers,
        json={"body": "Initial comment"},
    )
    assert created.status_code == 201, created.text
    comment = created.json()
    assert comment["todo_id"] == todo["id"]
    assert comment["author_id"] == account["user"]["id"]
    assert comment["body"] == "Initial comment"

    listed = client.get(f"/api/todos/{todo['id']}/comments", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == comment["id"]

    updated = client.patch(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers=headers,
        json={"body": "Updated comment"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["body"] == "Updated comment"

    deleted = client.delete(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers=headers,
    )
    assert deleted.status_code == 204
    assert (
        client.get(f"/api/todos/{todo['id']}/comments", headers=headers).json()["total"]
        == 0
    )


def test_deleting_todo_removes_its_comments(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
    database,
) -> None:
    account = register_user("comment-cascade@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    todo = create_todo(account["access_token"])
    create_comment(account["access_token"], todo["id"])

    response = client.delete(f"/api/todos/{todo['id']}", headers=headers)

    assert response.status_code == 204
    assert database["comments"].count_documents({"todo_id": todo["id"]}) == 0
