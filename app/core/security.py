from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()
_DUMMY_PASSWORD_HASH = password_hash.hash("not-a-real-user-password")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def verify_dummy_password(password: str) -> None:
    password_hash.verify(password, _DUMMY_PASSWORD_HASH)


def _jwt_secret() -> str:
    secret = settings.jwt_secret_key.get_secret_value()
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 characters.")
    return secret


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "token_use": "access",
            "jti": uuid4().hex,
        },
        _jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(subject: str) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    token_id = uuid4().hex
    token = jwt.encode(
        {
            "sub": subject,
            "iat": now,
            "exp": expires_at,
            "token_use": "refresh",
            "jti": token_id,
        },
        _jwt_secret(),
        algorithm=settings.jwt_algorithm,
    )
    return token, token_id, expires_at


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
    except jwt.InvalidTokenError:
        return None

    subject = payload.get("sub")
    if payload.get("token_use", "access") != "access":
        return None
    return subject if isinstance(subject, str) else None


def decode_refresh_token(token: str) -> tuple[str, str] | None:
    try:
        payload = jwt.decode(
            token,
            _jwt_secret(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub", "token_use", "jti"]},
        )
    except jwt.InvalidTokenError:
        return None

    subject = payload.get("sub")
    token_id = payload.get("jti")
    if (
        payload.get("token_use") != "refresh"
        or not isinstance(subject, str)
        or not isinstance(token_id, str)
    ):
        return None
    return subject, token_id
