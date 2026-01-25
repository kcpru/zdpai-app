from datetime import datetime
from typing import List
from uuid import UUID

from app.schemas.base import BaseSchema


class TodoListCreateRequest(BaseSchema):
    name: str


class TodoListUpdateRequest(BaseSchema):
    name: str


class TodoTaskCreateRequest(BaseSchema):
    title: str
    description: str | None = None


class TodoTaskUpdateRequest(BaseSchema):
    title: str
    description: str | None = None
    is_completed: bool


class TodoTaskPatchRequest(BaseSchema):
    is_completed: bool | None = None


class TodoTaskResponse(BaseSchema):
    id: UUID
    todo_list_id: UUID
    title: str
    description: str | None
    is_completed: bool


class TodoListResponse(BaseSchema):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    items: List[TodoTaskResponse]
