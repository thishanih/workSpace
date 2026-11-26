from typing import Any

from pymongo.database import Database

from app.modules.comments.schemas import CommentCreate, CommentRead, CommentUpdate
from app.modules.comments.service import (
    create_comment,
    delete_comment,
    list_comments,
    update_comment,
)


def add_comment(
    database: Database,
    todo_id: str,
    owner_id: str,
    payload: CommentCreate,
) -> CommentRead:
    return create_comment(database, todo_id, owner_id, payload)


def get_comments(
    database: Database,
    todo_id: str,
    owner_id: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    return list_comments(database, todo_id, owner_id, page, page_size)


def edit_comment(
    database: Database,
    todo_id: str,
    comment_id: str,
    owner_id: str,
    payload: CommentUpdate,
) -> CommentRead:
    return update_comment(
        database,
        todo_id,
        comment_id,
        owner_id,
        payload,
    )


def remove_comment(
    database: Database,
    todo_id: str,
    comment_id: str,
    owner_id: str,
) -> None:
    delete_comment(database, todo_id, comment_id, owner_id)
