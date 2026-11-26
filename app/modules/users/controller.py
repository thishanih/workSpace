from typing import Any

from pymongo.database import Database

from app.modules.users.schemas import UserRead, UserUpdate
from app.modules.users.service import get_user, update_user


def read_profile(user: dict[str, Any]) -> UserRead:
    return get_user(user)


def edit_profile(
    database: Database,
    user: dict[str, Any],
    payload: UserUpdate,
) -> UserRead:
    return update_user(database, user, payload)
