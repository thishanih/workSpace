from fastapi.testclient import TestClient


def test_register_returns_user_and_token_pair(client: TestClient) -> None:
    response = client.post(
        "/api/auth/register",
        json={
            "email": "register@example.com",
            "name": "Register User",
            "password": "valid-password",
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["token_type"] == "bearer"
    assert payload["user"]["email"] == "register@example.com"
    assert payload["user"]["name"] == "Register User"
    assert "password_hash" not in payload["user"]


def test_login_returns_user_and_token_pair(
    client: TestClient,
    register_user,
) -> None:
    registered = register_user("login@example.com")

    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "valid-password"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["user"]["id"] == registered["user"]["id"]
