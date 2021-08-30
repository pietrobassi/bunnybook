from typing import Dict, Optional
from uuid import UUID

import bcrypt
from asyncpg import UniqueViolationError
from injector import singleton, inject
from sqlalchemy import insert, select, update

from auth.exceptions import EmailAlreadyTaken, UsernameAlreadyTaken
from auth.models import profile, Profile, JwtRefreshToken, jwt_refresh_token
from common.concurrency import cpu_bound_task
from database.core import db
from database.graph import AsyncGraphDatabase
from database.utils import map_result


@singleton
class AuthRepo:
    @inject
    def __init__(self, graph_db: AsyncGraphDatabase):
        self._graph_db = graph_db

    @map_result
    @db.transaction()
    async def save_profile(self, new_profile: Profile) -> Profile:
        new_profile.password = (await cpu_bound_task(
            bcrypt.hashpw,
            new_profile.password.encode(),
            bcrypt.gensalt())).decode()
        new_profile.email = new_profile.email.lower()
        try:
            result = await db.fetch_one(insert(profile).values(
                new_profile.dict(exclude_none=True)).returning(profile))
            await self._graph_db.write_tx(lambda tx: tx.run(f"""
            CREATE (p:Profile {{id: '{result["id"]}', \
            username: '{result["username"]}'}})"""))
            return result
        except UniqueViolationError as e:
            if e.constraint_name == "profile_email_key":
                raise EmailAlreadyTaken()
            if e.constraint_name == "profile_username_key":
                raise UsernameAlreadyTaken()
            raise e

    @map_result
    async def find_profile_by_id(self, profile_id: UUID) -> Optional[Profile]:
        return await db.fetch_one(select([profile])
                                  .where(profile.c.id == profile_id))

    @map_result
    async def find_profile_by_email(self, email: str) -> Optional[Profile]:
        return await db.fetch_one(select([profile])
                                  .where(profile.c.email == email.lower()))

    @map_result
    async def find_jwt_refresh_token(self, token_id: UUID) \
            -> Optional[JwtRefreshToken]:
        return await db.fetch_one(select([jwt_refresh_token])
                                  .where(jwt_refresh_token.c.id == token_id))

    @map_result
    async def save_jwt_refresh_token(
            self,
            new_token: JwtRefreshToken) -> JwtRefreshToken:
        return await db.fetch_one(insert(jwt_refresh_token)
                                  .values(**new_token.dict(exclude_none=True))
                                  .returning(jwt_refresh_token))

    @map_result
    async def update_jwt_refresh_token(self, token_id: UUID, values: Dict) \
            -> JwtRefreshToken:
        return await db.fetch_one(update(jwt_refresh_token)
                                  .where(jwt_refresh_token.c.id == token_id)
                                  .values(**values)
                                  .returning(jwt_refresh_token))
