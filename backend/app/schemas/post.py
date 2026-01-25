from datetime import datetime
from typing import List
from uuid import UUID

from app.schemas.base import BaseSchema


class CreatePostRequest(BaseSchema):
    todo_list_id: UUID
    content: str


class CreatePostCommentRequest(BaseSchema):
    comment_text: str


class LikePostRequest(BaseSchema):
    likes_count: int


class LikePostCommentRequest(BaseSchema):
    likes_count: int


class PostCommentResponse(BaseSchema):
    id: UUID
    post_id: UUID
    user_id: UUID
    comment_text: str
    likes_count: int


class PostResponse(BaseSchema):
    id: UUID
    todo_list_as_json: str
    content: str
    likes_count: int
    created_at: datetime
    updated_at: datetime
    comments: List[PostCommentResponse]
