from typing import Any

from pymongo.database import Database

from app.modules.activities.schemas import ActivityRead
from app.modules.activities.service import get_activity, list_activities


def get_activity_list(
    database: Database,
    owner_id: str,
    page: int,
    page_size: int,
    todo_id: str | None,
) -> dict[str, Any]:
    return list_activities(database, owner_id, page, page_size, todo_id)


def get_activity_by_id(
    database: Database,
    activity_id: str,
    owner_id: str,
) -> ActivityRead:
    return get_activity(database, activity_id, owner_id)
