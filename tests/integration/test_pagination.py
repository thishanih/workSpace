import pytest
from fastapi.testclient import TestClient


def test_list_endpoints_support_empty_results_and_page_boundaries(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("empty-lists@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    todos = client.get("/api/todos", headers=headers)
    activities = client.get("/api/activities", headers=headers)
    assert todos.status_code == 200
    assert todos.json()["items"] == []
    assert activities.status_code == 200
    assert activities.json()["items"] == []

    todo = client.post(
        "/api/todos",
        headers=headers,
        json={"title": "One todo"},
    ).json()
    comments = client.get(
        f"/api/todos/{todo['id']}/comments",
        headers=headers,
        params={"page": 2, "page_size": 100},
    )
    activity_page = client.get(
        "/api/activities",
        headers=headers,
        params={"page": 2, "page_size": 100},
    )
    assert comments.status_code == 200
    assert comments.json()["page"] == 2
    assert comments.json()["page_size"] == 100
    assert comments.json()["items"] == []
    assert activity_page.status_code == 200
    assert activity_page.json()["page"] == 2
    assert activity_page.json()["page_size"] == 100
    assert activity_page.json()["items"] == []


@pytest.mark.parametrize(
    ("page", "page_size"),
    [
        pytest.param("0", "20", id="page-zero"),
        pytest.param("1", "0", id="page-size-zero"),
        pytest.param("1", "101", id="page-size-over-100"),
    ],
)
def test_todo_comment_and_activity_lists_reject_invalid_pagination(
    client: TestClient,
    register_user,
    create_todo,
    page: str,
    page_size: str,
) -> None:
    account = register_user("invalid-pagination@example.com")
    token = account["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    todo = create_todo(token)
    params = {"page": page, "page_size": page_size}

    responses = [
        client.get("/api/todos", headers=headers, params=params),
        client.get(
            f"/api/todos/{todo['id']}/comments",
            headers=headers,
            params=params,
        ),
        client.get("/api/activities", headers=headers, params=params),
    ]

    assert [response.status_code for response in responses] == [422, 422, 422]
