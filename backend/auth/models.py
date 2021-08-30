import datetime as dt
import enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, String, Table, ForeignKey, Boolean, \
    Enum, Index, func

from database.core import metadata
from database.utils import uuid_pk, PgUUID


class Role(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


profile = Table(
    "profile", metadata,
    uuid_pk(),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("registered_at", DateTime(timezone=True),
           server_default=func.now()),
    Column("last_login_at", DateTime(timezone=True)),
    Column("password", String, nullable=False),
    Column("role", Enum(Role), nullable=False,
           server_default=f"{Role.USER.value}"),
    Index("username_idx",
          "username", postgresql_using='gin',
          postgresql_ops={
              "username": 'gin_trgm_ops',
          })
)

jwt_refresh_token = Table(
    "jwt_refresh_token", metadata,
    uuid_pk(),
    Column("profile_id", PgUUID,
           ForeignKey("profile.id", ondelete="CASCADE"),
           nullable=False),
    Column("issued_at", DateTime(timezone=True), nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("invalidated_at", DateTime(timezone=True)),
    Column("previous_token_id", String),
    Column("valid", Boolean, nullable=False, server_default="true"),
)


class User(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: Role


class Profile(BaseModel):
    id: Optional[UUID]
    username: str
    email: EmailStr
    registered_at: Optional[dt.datetime]
    last_login_at: Optional[dt.datetime]
    password: str
    role: Role = Role.USER


class JwtRefreshToken(BaseModel):
    id: Optional[UUID]
    profile_id: UUID
    issued_at: dt.datetime
    expires_at: dt.datetime
    invalidated_at: Optional[dt.datetime]
    previous_token_id: Optional[str]
    valid: bool = True


class JwtUser(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: Role


class JwtTokenPayload(BaseModel):
    iat: dt.datetime
    exp: dt.datetime
    user: JwtUser


class JwtRefreshTokenPayload(BaseModel):
    iat: dt.datetime
    exp: dt.datetime
    jti: str
    profile_id: str


class JwtTokenData(BaseModel):
    access_token: str
    access_exp: int


class JwtRefreshTokenData(BaseModel):
    refresh_token: str
    refresh_exp: int


class JwtData(JwtTokenData, JwtRefreshTokenData):
    pass
