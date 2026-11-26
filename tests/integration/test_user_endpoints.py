from fastapi.testclient import TestClient


def test_user_profile_can_be_read_and_updated(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("profile@example.com", name="Original Name")
    headers = {"Authorization": f"Bearer {account['access_token']}"}

    profile = client.get("/api/users/me", headers=headers)
    assert profile.status_code == 200, profile.text
    assert profile.json()["id"] == account["user"]["id"]
    assert profile.json()["name"] == "Original Name"
    assert "password_hash" not in profile.json()

    updated = client.patch(
        "/api/users/me",
        headers=headers,
        json={"name": "Updated Name"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["name"] == "Updated Name"
    assert client.get("/api/users/me", headers=headers).json()["name"] == "Updated Name"
