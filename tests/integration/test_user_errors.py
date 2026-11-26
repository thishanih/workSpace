import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "name",
    [
        pytest.param("", id="empty-name"),
        pytest.param("   ", id="whitespace-name"),
        pytest.param("x" * 101, id="name-over-100"),
    ],
)
def test_profile_update_rejects_invalid_name(
    client: TestClient,
    register_user,
    database,
    name: str,
) -> None:
    account = register_user("invalid-profile@example.com")
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    response = client.patch("/api/users/me", headers=headers, json={"name": name})

    assert response.status_code == 422, response.text
    stored = database["users"].find_one({"email": "invalid-profile@example.com"})
    assert stored["name"] == "Test User"


def test_profile_is_scoped_to_authenticated_user(
    client: TestClient,
    register_user,
) -> None:
    first = register_user("profile-first@example.com", name="First User")
    second = register_user("profile-second@example.com", name="Second User")

    first_profile = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {first['access_token']}"},
    )
    second_profile = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    )

    assert first_profile.json()["id"] == first["user"]["id"]
    assert first_profile.json()["name"] == "First User"
    assert second_profile.json()["id"] == second["user"]["id"]
    assert second_profile.json()["name"] == "Second User"
