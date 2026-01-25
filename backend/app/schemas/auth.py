from app.schemas.base import BaseSchema


class RegisterRequest(BaseSchema):
    username: str
    email: str
    password: str


class LoginRequest(BaseSchema):
    username_or_email: str
    password: str


class AuthResponse(BaseSchema):
    access_token: str
