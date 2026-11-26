import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("", id="empty-body"),
        pytest.param("   ", id="whitespace-body"),
        pytest.param("x" * 2001, id="body-over-2000"),
    ],
)
def test_comment_creation_rejects_invalid_body(
    client: TestClient,
    register_user,
    create_todo,
    database,
    body: str,
) -> None:
    account = register_user("invalid-comment@example.com")
    todo = create_todo(account["access_token"])
    before = database["comments"].count_documents({})

    response = client.post(
        f"/api/todos/{todo['id']}/comments",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json={"body": body},
    )

    assert response.status_code == 422, response.text
    assert database["comments"].count_documents({}) == before


def test_comment_update_rejects_invalid_body_without_mutation(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
    database,
) -> None:
    account = register_user("invalid-comment-update@example.com")
    todo = create_todo(account["access_token"])
    comment = create_comment(account["access_token"], todo["id"], "Original")

    response = client.patch(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json={"body": " "},
    )

    assert response.status_code == 422, response.text
    stored = database["comments"].find_one({"todo_id": todo["id"], "body": "Original"})
    assert stored is not None


@pytest.mark.parametrize(
    ("todo_id", "comment_id"),
    [
        pytest.param("bad-id", "bad-id", id="malformed-ids"),
        pytest.param(
            "64a000000000000000000001",
            "64a000000000000000000002",
            id="well-formed-absent-ids",
        ),
    ],
)
@pytest.mark.parametrize(
    ("method", "payload"),
    [
        pytest.param("GET", None, id="list-comments"),
        pytest.param("POST", {"body": "Comment"}, id="create-comment"),
        pytest.param("PATCH", {"body": "Changed"}, id="update-comment"),
        pytest.param("DELETE", None, id="delete-comment"),
    ],
)
def test_comment_operations_reject_missing_resources(
    client: TestClient,
    register_user,
    todo_id: str,
    comment_id: str,
    method: str,
    payload: dict[str, str] | None,
) -> None:
    account = register_user("missing-comment@example.com")
    path = f"/api/todos/{todo_id}/comments"
    if method in {"PATCH", "DELETE"}:
        path += f"/{comment_id}"

    response = client.request(
        method,
        path,
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json=payload,
    )

    assert response.status_code == 404, response.text


def test_other_user_cannot_access_todo_comments(
    client: TestClient,
    register_user,
    create_todo,
    create_comment,
    database,
) -> None:
    owner = register_user("comment-owner@example.com")
    other = register_user("comment-other@example.com")
    todo = create_todo(owner["access_token"])
    comment = create_comment(owner["access_token"], todo["id"], "Private comment")
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}
    before = database["comments"].count_documents({})

    listed = client.get(f"/api/todos/{todo['id']}/comments", headers=other_headers)
    created = client.post(
        f"/api/todos/{todo['id']}/comments",
        headers=other_headers,
        json={"body": "Unauthorized"},
    )
    updated = client.patch(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers=other_headers,
        json={"body": "Unauthorized"},
    )
    deleted = client.delete(
        f"/api/todos/{todo['id']}/comments/{comment['id']}",
        headers=other_headers,
    )

    assert [
        listed.status_code,
        created.status_code,
        updated.status_code,
        deleted.status_code,
    ] == [
        404,
        404,
        404,
        404,
    ]
    assert database["comments"].count_documents({}) == before
    stored = database["comments"].find_one({"body": "Private comment"})
    assert stored is not None
    assert stored["todo_id"] == todo["id"]


@pytest.mark.parametrize(
    "comment_id",
    [
        pytest.param("malformed", id="malformed-comment-id"),
        pytest.param("64a000000000000000000002", id="absent-comment-id"),
    ],
)
@pytest.mark.parametrize("method", ["PATCH", "DELETE"])
def test_comment_mutations_reject_missing_comment(
    client: TestClient,
    register_user,
    create_todo,
    comment_id: str,
    method: str,
) -> None:
    account = register_user("missing-comment-id@example.com")
    todo = create_todo(account["access_token"])
    response = client.request(
        method,
        f"/api/todos/{todo['id']}/comments/{comment_id}",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json={"body": "Changed"} if method == "PATCH" else None,
    )

    assert response.status_code == 404, response.text
