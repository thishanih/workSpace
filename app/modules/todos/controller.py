from typing import Any

from pymongo.database import Database

from app.modules.todos.schemas import TodoCreate, TodoRead, TodoUpdate
from app.modules.todos.service import (
    create_todo,
    delete_todo,
    list_todos,
    read_todo,
    update_todo,
)


def add_todo(
    database: Database,
    owner_id: str,
    payload: TodoCreate,
) -> TodoRead:
    return create_todo(database, owner_id, payload)


def get_todos(
    database: Database,
    owner_id: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    return list_todos(database, owner_id, page, page_size)


def get_todo(database: Database, todo_id: str, owner_id: str) -> TodoRead:
    return read_todo(database, todo_id, owner_id)


def edit_todo(
    database: Database,
    todo_id: str,
    owner_id: str,
    payload: TodoUpdate,
) -> TodoRead:
    return update_todo(database, todo_id, owner_id, payload)


def remove_todo(database: Database, todo_id: str, owner_id: str) -> None:
    delete_todo(database, todo_id, owner_id)
