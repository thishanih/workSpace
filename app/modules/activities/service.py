from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.database import Database

from app.core.exceptions import AppError
from app.modules.activities.models import COLLECTION_NAME
from app.modules.activities.schemas import ActivityRead
from app.utils.ids import parse_object_id
from app.utils.pagination import paginate_collection
from app.utils.response import serialize_document


def record_activity(
    database: Database,
    *,
    owner_id: str,
    actor_id: str,
    todo_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    summary: str,
) -> None:
    database[COLLECTION_NAME].insert_one(
        {
            "owner_id": owner_id,
            "actor_id": actor_id,
            "todo_id": todo_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "summary": summary,
            "created_at": datetime.now(timezone.utc),
        }
    )


def _activity_read(document: dict[str, Any]) -> ActivityRead:
    return ActivityRead.model_validate(serialize_document(document))


def list_activities(
    database: Database,
    owner_id: str,
    page: int,
    page_size: int,
    todo_id: str | None,
) -> dict[str, Any]:
    query: dict[str, Any] = {"owner_id": owner_id}
    if todo_id is not None:
        todo_object_id = parse_object_id(todo_id, "Todo")
        if (
            database["todos"].find_one({"_id": todo_object_id, "owner_id": owner_id})
            is None
        ):
            raise AppError(404, "Todo not found.")
        query["todo_id"] = str(todo_object_id)

    return paginate_collection(
        database[COLLECTION_NAME],
        query,
        page,
        page_size,
        _activity_read,
    )


def get_activity(database: Database, activity_id: str, owner_id: str) -> ActivityRead:
    object_id: ObjectId = parse_object_id(activity_id, "Activity")
    document = database[COLLECTION_NAME].find_one(
        {"_id": object_id, "owner_id": owner_id}
    )
    if document is None:
        raise AppError(404, "Activity not found.")
    return _activity_read(document)
