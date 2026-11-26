from typing import Any

from fastapi import APIRouter, Depends
from pymongo.database import Database

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database
from app.modules.activities.controller import get_activity_by_id, get_activity_list
from app.modules.activities.schemas import ActivityRead
from app.utils.validation import PageNumber, PageSize

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("")
def list_user_activities(
    page: PageNumber = 1,
    page_size: PageSize = 20,
    todo_id: str | None = None,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    return get_activity_list(
        database,
        str(user["_id"]),
        page,
        page_size,
        todo_id,
    )


@router.get("/{activity_id}", response_model=ActivityRead)
def get_user_activity(
    activity_id: str,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> ActivityRead:
    return get_activity_by_id(database, activity_id, str(user["_id"]))
