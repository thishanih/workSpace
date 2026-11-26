import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "activity_id",
    [
        pytest.param("not-an-object-id", id="malformed-id"),
        pytest.param("64a000000000000000000001", id="well-formed-absent-id"),
    ],
)
def test_activity_read_rejects_missing_resource(
    client: TestClient,
    register_user,
    activity_id: str,
) -> None:
    account = register_user("missing-activity@example.com")

    response = client.get(
        f"/api/activities/{activity_id}",
        headers={"Authorization": f"Bearer {account['access_token']}"},
    )

    assert response.status_code == 404, response.text


def test_activity_list_and_read_are_scoped_to_owner(
    client: TestClient,
    register_user,
    create_todo,
    database,
) -> None:
    owner = register_user("activity-owner@example.com")
    other = register_user("activity-other@example.com")
    todo = create_todo(owner["access_token"], title="Private activity todo")
    owner_headers = {"Authorization": f"Bearer {owner['access_token']}"}
    other_headers = {"Authorization": f"Bearer {other['access_token']}"}
    activity = client.get("/api/activities", headers=owner_headers).json()["items"][0]

    other_list = client.get("/api/activities", headers=other_headers)
    other_read = client.get(
        f"/api/activities/{activity['id']}",
        headers=other_headers,
    )

    assert other_list.status_code == 200
    assert other_list.json()["total"] == 0
    assert other_read.status_code == 404
    stored = database["todos"].find_one({"title": "Private activity todo"})
    assert stored is not None
    filtered = client.get(
        "/api/activities",
        headers=owner_headers,
        params={"todo_id": todo["id"]},
    )
    assert filtered.status_code == 200


@pytest.mark.parametrize(
    "todo_id",
    [
        pytest.param("malformed", id="malformed-todo-filter"),
        pytest.param("64a000000000000000000001", id="absent-todo-filter"),
    ],
)
def test_activity_filter_rejects_invalid_or_missing_todo(
    client: TestClient,
    register_user,
    todo_id: str,
) -> None:
    account = register_user("activity-filter@example.com")

    response = client.get(
        "/api/activities",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        params={"todo_id": todo_id},
    )

    assert response.status_code == 404, response.text
