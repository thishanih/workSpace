from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo.database import Database

from app.core.exceptions import AppError
from app.modules.activities.service import record_activity
from app.modules.comments.models import COLLECTION_NAME
from app.modules.comments.schemas import CommentCreate, CommentRead, CommentUpdate
from app.modules.todos.service import get_owned_todo
from app.utils.ids import parse_object_id
from app.utils.pagination import paginate_collection
from app.utils.response import serialize_document


def _comment_read(document: dict[str, Any]) -> CommentRead:
    return CommentRead.model_validate(serialize_document(document))


def create_comment(
    database: Database,
    todo_id: str,
    owner_id: str,
    payload: CommentCreate,
) -> CommentRead:
    todo = get_owned_todo(database, todo_id, owner_id)
    now = datetime.now(timezone.utc)
    document = {
        "todo_id": str(todo["_id"]),
        "owner_id": owner_id,
        "author_id": owner_id,
        "body": payload.body,
        "created_at": now,
        "updated_at": now,
    }
    result = database[COLLECTION_NAME].insert_one(document)
    document["_id"] = result.inserted_id
    comment_id = str(result.inserted_id)
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="created",
        entity_type="comment",
        entity_id=comment_id,
        summary=f"Added a comment to todo: {todo['title']}",
    )
    return _comment_read(document)


def list_comments(
    database: Database,
    todo_id: str,
    owner_id: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    todo = get_owned_todo(database, todo_id, owner_id)
    return paginate_collection(
        database[COLLECTION_NAME],
        {"todo_id": str(todo["_id"]), "owner_id": owner_id},
        page,
        page_size,
        _comment_read,
    )


def update_comment(
    database: Database,
    todo_id: str,
    comment_id: str,
    owner_id: str,
    payload: CommentUpdate,
) -> CommentRead:
    todo = get_owned_todo(database, todo_id, owner_id)
    object_id: ObjectId = parse_object_id(comment_id, "Comment")
    query = {
        "_id": object_id,
        "todo_id": str(todo["_id"]),
        "owner_id": owner_id,
    }
    comment = database[COLLECTION_NAME].find_one(query)
    if comment is None:
        raise AppError(404, "Comment not found.")

    database[COLLECTION_NAME].update_one(
        query,
        {
            "$set": {
                "body": payload.body,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    updated = database[COLLECTION_NAME].find_one(query)
    if updated is None:
        raise RuntimeError("The comment disappeared during an update.")
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="updated",
        entity_type="comment",
        entity_id=comment_id,
        summary=f"Updated a comment on todo: {todo['title']}",
    )
    return _comment_read(updated)


def delete_comment(
    database: Database,
    todo_id: str,
    comment_id: str,
    owner_id: str,
) -> None:
    todo = get_owned_todo(database, todo_id, owner_id)
    object_id: ObjectId = parse_object_id(comment_id, "Comment")
    query = {
        "_id": object_id,
        "todo_id": str(todo["_id"]),
        "owner_id": owner_id,
    }
    comment = database[COLLECTION_NAME].find_one(query)
    if comment is None:
        raise AppError(404, "Comment not found.")
    database[COLLECTION_NAME].delete_one(query)
    record_activity(
        database,
        owner_id=owner_id,
        actor_id=owner_id,
        todo_id=todo_id,
        action="deleted",
        entity_type="comment",
        entity_id=comment_id,
        summary=f"Deleted a comment from todo: {todo['title']}",
    )
