from datetime import datetime, timezone

from bson import ObjectId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from app.core.exceptions import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_dummy_password,
    verify_password,
)
from app.modules.auth.models import REFRESH_TOKEN_COLLECTION, USER_COLLECTION
from app.modules.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.modules.users.schemas import UserRead


def _user_read(document: dict) -> UserRead:
    return UserRead(
        id=str(document["_id"]),
        email=document["email"],
        name=document["name"],
        created_at=document["created_at"],
    )


def _token_response(database: Database, user: dict) -> TokenResponse:
    user_id = str(user["_id"])
    refresh_token, token_id, expires_at = create_refresh_token(user_id)
    database[REFRESH_TOKEN_COLLECTION].insert_one(
        {
            "_id": token_id,
            "user_id": user_id,
            "expires_at": expires_at,
        }
    )
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=refresh_token,
        user=_user_read(user),
    )


def register_user(database: Database, payload: RegisterRequest) -> TokenResponse:
    now = datetime.now(timezone.utc)
    user_id = ObjectId()
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

    return _token_response(database, document)


def login_user(database: Database, payload: LoginRequest) -> TokenResponse:
    email = str(payload.email).lower()
    document = database[USER_COLLECTION].find_one({"email": email})
    if document is None:
        verify_dummy_password(payload.password)
        raise AppError(401, "Email or password is incorrect.")
    if not verify_password(payload.password, document["password_hash"]):
        raise AppError(401, "Email or password is incorrect.")

    return _token_response(database, document)


def refresh_user_tokens(
    database: Database,
    payload: RefreshRequest,
) -> TokenResponse:
    decoded = decode_refresh_token(payload.refresh_token)
    if decoded is None:
        raise AppError(401, "Refresh token is invalid or expired.")

    user_id, token_id = decoded
    if not ObjectId.is_valid(user_id):
        raise AppError(401, "Refresh token is invalid or expired.")

    user = database[USER_COLLECTION].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise AppError(401, "Refresh token is invalid or expired.")

    now = datetime.now(timezone.utc)
    consumed = database[REFRESH_TOKEN_COLLECTION].delete_one(
        {
            "_id": token_id,
            "user_id": user_id,
            "expires_at": {"$gt": now},
        }
    )
    if consumed.deleted_count != 1:
        raise AppError(401, "Refresh token is invalid or expired.")

    return _token_response(database, user)
