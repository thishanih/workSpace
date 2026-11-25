from typing import Any

from bson import ObjectId
from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.database import Database

from app.core.database import get_database
from app.core.exceptions import AppError

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    database: Database = Depends(get_database),
) -> dict[str, Any]:
    user_id = getattr(request.state, "user_id", None)
    if user_id is None and credentials is not None:
        from app.core.security import decode_access_token

        user_id = decode_access_token(credentials.credentials)

    if user_id is None or not ObjectId.is_valid(user_id):
        raise AppError(401, "A valid bearer token is required.")

    user = database["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise AppError(401, "The authenticated user no longer exists.")
    return user
