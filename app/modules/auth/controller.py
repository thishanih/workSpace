from pymongo.database import Database

from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.auth.service import login_user, register_user


def register(database: Database, payload: RegisterRequest) -> TokenResponse:
    return register_user(database, payload)


def login(database: Database, payload: LoginRequest) -> TokenResponse:
    return login_user(database, payload)
