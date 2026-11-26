from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.database import Database

from app.core.exceptions import AppError
from app.modules.activities.service import record_activity
from app.modules.todos.models import COLLECTION_NAME
from app.modules.todos.schemas import TodoCreate, TodoRead, TodoUpdate
from app.utils.ids import parse_object_id
from app.utils.pagination import paginate_collection
from app.utils.response import serialize_document


def _todo_read(document: dict[str, Any]) -> TodoRead:
    return TodoRead.model_validate(serialize_document(document))


def get_owned_todo(
    database: Database,
    todo_id: str,
    owner_id: str,
) -> dict[str, Any]:
    object_id: ObjectId = parse_object_id(todo_id, "Todo")
    document = database[COLLECTION_NAME].find_one(
        {"_id": object_id, "owner_id": owner_id}
    )
    if document is None:
        raise AppError(404, "Todo not found.")
    return document


def create_todo(
    database: Database,
    owner_id: str,
    payload: TodoCreate,
) -> TodoRead:
    now = datetime.now(timezone.utc)
    document = {
        "owner_id": owner_id,
        **payload.model_dump(mode="json"),
        "created_at": now,
        "updated_at": now,
    }
    result = database[COLLECTION_NAME].insert_one(document)
    document["_id"] = result.inserted_id
    todo_id = str(result.inserted_id)
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="created",
        entity_type="todo",
        entity_id=todo_id,
        summary=f"Created todo: {payload.title}",
    )
    return _todo_read(document)


def list_todos(
    database: Database,
    owner_id: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    return paginate_collection(
        database[COLLECTION_NAME],
        {"owner_id": owner_id},
        page,
        page_size,
        _todo_read,
    )


def read_todo(database: Database, todo_id: str, owner_id: str) -> TodoRead:
    return _todo_read(get_owned_todo(database, todo_id, owner_id))


def update_todo(
    database: Database,
    todo_id: str,
    owner_id: str,
    payload: TodoUpdate,
) -> TodoRead:
    document = get_owned_todo(database, todo_id, owner_id)
    changes = payload.model_dump(mode="json", exclude_unset=True)
    changes["updated_at"] = datetime.now(timezone.utc)
    database[COLLECTION_NAME].update_one(
        {"_id": document["_id"], "owner_id": owner_id},
        {"$set": changes},
    )
    updated = database[COLLECTION_NAME].find_one({"_id": document["_id"]})
    if updated is None:
        raise RuntimeError("The todo disappeared during an update.")
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="updated",
        entity_type="todo",
        entity_id=todo_id,
        summary=f"Updated todo: {updated['title']}",
    )
    return _todo_read(updated)


def delete_todo(database: Database, todo_id: str, owner_id: str) -> None:
    document = get_owned_todo(database, todo_id, owner_id)
    database[COLLECTION_NAME].delete_one({"_id": document["_id"], "owner_id": owner_id})
    database["comments"].delete_many({"todo_id": todo_id, "owner_id": owner_id})
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="deleted",
        entity_type="todo",
        entity_id=todo_id,
        summary=f"Deleted todo: {document['title']}",
    )
