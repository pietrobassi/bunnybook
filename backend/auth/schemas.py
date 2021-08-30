from uuid import UUID, uuid4

from pydantic import Field, EmailStr

from auth.models import Role
from common.schemas import BaseSchema


class ProfileCreate(BaseSchema):
    username: str = Field(
        min_length=2,
        max_length=32,
        regex="^[a-zA-Z0-9]+([-_.][a-zA-Z0-9]+)*$")
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    avatar_identifier: str = str(uuid4())


class RegisterResponse(BaseSchema):
    id: UUID
    username: str
    email: EmailStr
    role: Role


class LoginIn(BaseSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class LoginResponse(BaseSchema):
    access_token: str
    access_exp: int
    refresh_exp: int
