from app.schemas.base import BaseSchema
from uuid import UUID


class MeResponse(BaseSchema):
    id: UUID
    username: str
    email: str
    is_admin: bool


class UserResponse(BaseSchema):
    username: str


class UpdateProfileRequest(BaseSchema):
    username: str
    email: str


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str


class AdminUserResponse(BaseSchema):
    id: UUID
    username: str
    email: str
    is_admin: bool


class AdminUserUpdateRequest(BaseSchema):
    username: str | None = None
    email: str | None = None
    is_admin: bool | None = None
