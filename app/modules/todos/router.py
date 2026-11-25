from typing import Any

from fastapi import APIRouter, Depends, Query, Response, status
from pymongo.database import Database

from app.dependencies.auth import get_current_user
from app.dependencies.database import get_database
from app.modules.todos.controller import (
    add_todo,
    edit_todo,
    get_todo,
    get_todos,
    remove_todo,
)
from app.modules.todos.schemas import TodoCreate, TodoRead, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
def create_todo(
    payload: TodoCreate,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> TodoRead:
    return add_todo(database, str(user["_id"]), payload)


@router.get("")
def list_todos(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    return get_todos(database, str(user["_id"]), page, page_size)


@router.get("/{todo_id}", response_model=TodoRead)
def get_todo_by_id(
    todo_id: str,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> TodoRead:
    return get_todo(database, todo_id, str(user["_id"]))


@router.patch("/{todo_id}", response_model=TodoRead)
def update_todo_by_id(
    todo_id: str,
    payload: TodoUpdate,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> TodoRead:
    return edit_todo(database, todo_id, str(user["_id"]), payload)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo_by_id(
    todo_id: str,
    database: Database = Depends(get_database),
    user: dict[str, Any] = Depends(get_current_user),
) -> Response:
    remove_todo(database, todo_id, str(user["_id"]))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
