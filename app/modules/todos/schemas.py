from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TodoStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TodoCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TodoStatus = TodoStatus.pending


class TodoUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: TodoStatus | None = None

    @field_validator("title", "status", mode="before")
    @classmethod
    def disallow_null_updates(cls, value: object) -> object:
        if value is None:
            raise ValueError("This field cannot be null.")
        return value

    @model_validator(mode="after")
    def require_update(self) -> "TodoUpdate":
        if not self.model_fields_set:
            raise ValueError("Provide at least one field to update.")
        return self


class TodoRead(BaseModel):
    id: str
    title: str
    description: str | None
    status: TodoStatus
    created_at: datetime
    updated_at: datetime
