from typing import Any

from fastapi import APIRouter, Depends
from pymongo.database import Database

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database
from app.modules.users.controller import edit_profile, read_profile
from app.modules.users.schemas import UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_profile(user: dict[str, Any] = Depends(get_current_user)) -> UserRead:
    return read_profile(user)


@router.patch("/me", response_model=UserRead)
def update_profile(
    payload: UserUpdate,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> UserRead:
    return edit_profile(database, user, payload)
