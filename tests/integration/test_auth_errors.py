from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"email": "not-an-email", "name": "User", "password": "valid-password"},
            id="invalid-email",
        ),
        pytest.param(
            {
                "email": "invalid-name@example.com",
                "name": " ",
                "password": "valid-password",
            },
            id="blank-name",
        ),
        pytest.param(
            {
                "email": "short-password@example.com",
                "name": "User",
                "password": "short",
            },
            id="short-password",
        ),
    ],
)
def test_registration_rejects_invalid_account_fields(
    client: TestClient,
    payload: dict[str, str],
) -> None:
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 422, response.text


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param(
            {"email": "unknown@example.com", "password": "valid-password"},
            id="unknown-email",
        ),
        pytest.param(
            {"email": "known@example.com", "password": "wrong-password"},
            id="wrong-password",
        ),
    ],
)
def test_login_rejects_invalid_credentials(
    client: TestClient,
    register_user,
    payload: dict[str, str],
) -> None:
    register_user("known@example.com")

    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 401, response.text


@pytest.mark.parametrize(
    ("refresh_token", "expected_status"),
    [
        pytest.param("not-a-token", 401, id="malformed"),
        pytest.param("", 422, id="empty"),
    ],
)
def test_refresh_rejects_invalid_refresh_token(
    client: TestClient,
    refresh_token: str,
    expected_status: int,
) -> None:
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == expected_status, response.text


def test_refresh_rejects_expired_token(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("expired-refresh@example.com")
    expired = jwt.encode(
        {
            "sub": account["user"]["id"],
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "token_use": "refresh",
            "jti": "expired-refresh-token",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

    response = client.post("/api/auth/refresh", json={"refresh_token": expired})

    assert response.status_code == 401, response.text


def test_refresh_rejects_access_purpose_token(
    client: TestClient,
    register_user,
) -> None:
    account = register_user("wrong-purpose@example.com")
    access_token = account["access_token"]

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401, response.text
