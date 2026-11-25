from datetime import datetime, timezone

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    hash_password,
    verify_dummy_password,
    verify_password,
)
from app.modules.auth.models import USER_COLLECTION
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.users.schemas import UserRead


def _user_read(document: dict) -> UserRead:
    return UserRead(
        id=str(document["_id"]),
        email=document["email"],
        name=document["name"],
        created_at=document["created_at"],
    )


def register_user(database: Database, payload: RegisterRequest) -> TokenResponse:
    now = datetime.now(timezone.utc)
    user_id = ObjectId()
    access_token = create_access_token(str(user_id))
    document = {
        "_id": user_id,
        "email": str(payload.email).lower(),
        "name": payload.name,
        "password_hash": hash_password(payload.password),
        "created_at": now,
        "updated_at": now,
    }
    if database[USER_COLLECTION].find_one({"email": document["email"]}) is not None:
        raise AppError(409, "An account with this email already exists.")

    try:
        database[USER_COLLECTION].insert_one(document)
    except DuplicateKeyError as error:
        raise AppError(409, "An account with this email already exists.") from error

    return TokenResponse(
        access_token=access_token,
        user=_user_read(document),
    )


def login_user(database: Database, payload: LoginRequest) -> TokenResponse:
    email = str(payload.email).lower()
    document = database[USER_COLLECTION].find_one({"email": email})
    if document is None:
        verify_dummy_password(payload.password)
        raise AppError(401, "Email or password is incorrect.")
    if not verify_password(payload.password, document["password_hash"]):
        raise AppError(401, "Email or password is incorrect.")

    return TokenResponse(
        access_token=create_access_token(str(document["_id"])),
        user=_user_read(document),
    )
