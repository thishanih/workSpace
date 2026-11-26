from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.database import Database

from app.modules.users.models import COLLECTION_NAME
from app.modules.users.schemas import UserRead, UserUpdate


def get_user(user: dict[str, Any]) -> UserRead:
    return UserRead(
        id=str(user["_id"]),
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"],
    )


def update_user(
    database: Database,
    user: dict[str, Any],
    payload: UserUpdate,
) -> UserRead:
    database[COLLECTION_NAME].update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"name": payload.name, "updated_at": datetime.now(timezone.utc)}},
    )
    updated_user = database[COLLECTION_NAME].find_one({"_id": user["_id"]})
    if updated_user is None:
        raise RuntimeError("The authenticated user disappeared during an update.")
    return get_user(updated_user)
