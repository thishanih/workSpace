import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"title": ""}, id="empty-title"),
        pytest.param({"title": "   "}, id="whitespace-title"),
        pytest.param({"title": "x" * 201}, id="title-over-200"),
        pytest.param(
            {"title": "Valid", "description": "x" * 5001}, id="description-over-5000"
        ),
        pytest.param({"title": "Valid", "status": "unknown"}, id="invalid-status"),
    ],
)
def test_todo_creation_rejects_invalid_fields(
    client: TestClient,
    register_user,
    database,
    payload: dict[str, str],
) -> None:
    account = register_user("invalid-todo@example.com")
    before = database["todos"].count_documents({})

    response = client.post(
        "/api/todos",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json=payload,
    )

    assert response.status_code == 422, response.text
    assert database["todos"].count_documents({}) == before


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({}, id="empty-update"),
        pytest.param({"title": None}, id="null-title"),
        pytest.param({"status": None}, id="null-status"),
        pytest.param({"title": " "}, id="blank-title"),
    ],
)
def test_todo_update_rejects_invalid_fields_without_mutation(
    client: TestClient,
    register_user,
    create_todo,
    database,
    payload: dict[str, str | None],
) -> None:
    account = register_user("invalid-todo-update@example.com")
    token = account["access_token"]
    todo = create_todo(token, title="Original title")

    response = client.patch(
        f"/api/todos/{todo['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
    )

    assert response.status_code == 422, response.text
    stored = database["todos"].find_one({"title": "Original title"})
    assert stored is not None
    assert stored["title"] == "Original title"


@pytest.mark.parametrize(
    "todo_id",
    [
        pytest.param("not-an-object-id", id="malformed-id"),
        pytest.param("64a000000000000000000001", id="well-formed-absent-id"),
    ],
)
@pytest.mark.parametrize(
    ("method", "suffix", "payload"),
    [
        pytest.param("GET", "", None, id="read"),
        pytest.param("PATCH", "", {"title": "Changed"}, id="update"),
        pytest.param("DELETE", "", None, id="delete"),
    ],
)
def test_todo_operations_reject_missing_resource(
    client: TestClient,
    register_user,
    todo_id: str,
    method: str,
    suffix: str,
    payload: dict[str, str] | None,
) -> None:
    account = register_user("missing-todo@example.com")

    response = client.request(
        method,
        f"/api/todos/{todo_id}{suffix}",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        json=payload,
    )

    assert response.status_code == 404, response.text


def test_other_user_cannot_read_update_or_delete_todo(
    client: TestClient,
    register_user,
    create_todo,
    database,
) -> None:
    owner = register_user("todo-owner@example.com")
    other = register_user("todo-other@example.com")
    todo = create_todo(owner["access_token"], title="Private todo")
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}

    read = client.get(f"/api/todos/{todo['id']}", headers=other_headers)
    update = client.patch(
        f"/api/todos/{todo['id']}",
        headers=other_headers,
        json={"title": "Stolen"},
    )
    delete = client.delete(f"/api/todos/{todo['id']}", headers=other_headers)

    assert read.status_code == update.status_code == delete.status_code == 404
    stored = database["todos"].find_one({"title": "Private todo"})
    assert stored is not None
    assert stored["title"] == "Private todo"
    assert client.get("/api/todos", headers=other_headers).json()["total"] == 0
