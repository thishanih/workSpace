from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from pymongo.database import Database

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database
from app.modules.comments.controller import (
    add_comment,
    edit_comment,
    get_comments,
    remove_comment,
)
from app.modules.comments.schemas import CommentCreate, CommentRead, CommentUpdate

router = APIRouter(prefix="/todos/{todo_id}/comments", tags=["comments"])


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
def create_todo_comment(
    todo_id: str,
    payload: CommentCreate,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> CommentRead:
    return add_comment(database, todo_id, str(user["_id"]), payload)


@router.get("")
def list_todo_comments(
    todo_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    return get_comments(
        database,
        todo_id,
        str(user["_id"]),
        page,
        page_size,
    )


@router.patch("/{comment_id}", response_model=CommentRead)
def update_todo_comment(
    todo_id: str,
    comment_id: str,
    payload: CommentUpdate,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> CommentRead:
    return edit_comment(
        database,
        todo_id,
        comment_id,
        str(user["_id"]),
        payload,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_comment(
    todo_id: str,
    comment_id: str,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    remove_comment(database, todo_id, comment_id, str(user["_id"]))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
