import pytest
from fastapi.testclient import TestClient


def test_missing_registration_field_does_not_create_user(
    client: TestClient,
    database,
) -> None:
    before = database["users"].count_documents({})

    response = client.post(
        "/api/auth/register",
        json={"email": "missing-field@example.com", "name": "Missing Password"},
    )

    assert response.status_code == 422, response.text
    assert database["users"].count_documents({}) == before


def test_malformed_json_does_not_create_todo(
    client: TestClient,
    register_user,
    database,
) -> None:
    account = register_user("malformed-json@example.com")
    before = database["todos"].count_documents({})

    response = client.post(
        "/api/todos",
        headers={"Authorization": f"Bearer {account['access_token']}"},
        content='{"title":',
    )

    assert response.status_code == 422, response.text
    assert database["todos"].count_documents({}) == before


@pytest.mark.parametrize(
    "endpoint",
    ["todos", "comments", "activities"],
)
def test_list_endpoints_reject_non_integer_page(
    client: TestClient,
    register_user,
    create_todo,
    endpoint: str,
) -> None:
    account = register_user(f"invalid-page-{endpoint}@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}
    todo = create_todo(account["access_token"])
    path = {
        "todos": "/api/todos",
        "comments": f"/api/todos/{todo['id']}/comments",
        "activities": "/api/activities",
    }[endpoint]

    response = client.get(path, headers=headers, params={"page": "not-an-integer"})

    assert response.status_code == 422, response.text
