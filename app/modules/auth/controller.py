from pymongo.database import Database

from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.auth.service import login_user, refresh_user_tokens, register_user


def register(database: Database, payload: RegisterRequest) -> TokenResponse:
    return register_user(database, payload)


def login(database: Database, payload: LoginRequest) -> TokenResponse:
    return login_user(database, payload)


def refresh(database: Database, payload: RefreshRequest) -> TokenResponse:
    return refresh_user_tokens(database, payload)
