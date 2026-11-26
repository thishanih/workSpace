from datetime import datetime

from pydantic import BaseModel


class ActivityRead(BaseModel):
    id: str
    todo_id: str
    actor_id: str
    action: str
    entity_type: str
    entity_id: str
    summary: str
    created_at: datetime
