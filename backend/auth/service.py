import datetime as dt
from calendar import timegm
from typing import Optional
from uuid import UUID

import bcrypt
import jwt
from injector import singleton, inject

from auth.exceptions import LoginFailed, \
    ExpiredJwtRefreshToken, InvalidatedJwtRefreshToken
from auth.models import Profile, JwtTokenPayload, JwtUser, \
    JwtRefreshTokenPayload, JwtRefreshToken, JwtData, JwtTokenData, \
    JwtRefreshTokenData
from auth.repo import AuthRepo
from auth.security import decode_jwt_refresh_token
from common.concurrency import cpu_bound_task
from config import cfg
from database.core import db


@singleton
class AuthService:
    @inject
    def __init__(self, repo: AuthRepo):
        self._repo = repo

    async def register(self, profile: Profile) -> Profile:
        """
        Register a new user.

        :param profile: profile data
        :return: newly created profile
        """

        return await self._repo.save_profile(profile)

    async def login(self, email: str, password: str) -> JwtData:
        """
        Try to log the user in, using provided email and password.

        :param email: user's registered email
        :param password: user's (non-hashed) password
        :return: access_token, access_exp, refresh_token, refresh_exp
        """

        profile = await self._repo.find_profile_by_email(email=email)
        if not profile or not await self._check_password(password,
                                                         profile.password):
            raise LoginFailed()
        jwt_data = self._generate_jwt_access_token(profile)
        jwt_refresh_data = await self._generate_jwt_refresh_token(profile.id)
        return JwtData(access_token=jwt_data.access_token,
                       access_exp=jwt_data.access_exp,
                       refresh_token=jwt_refresh_data.refresh_token,
                       refresh_exp=jwt_refresh_data.refresh_exp)

    async def refresh_jwt_access_token(self,
                                       encoded_refresh_token: str) -> JwtData:
        """
        Perform jwt access token refreshing and refresh token rotation,
        returning a new jwt access token if provided refresh token is still
        valid (not expired and not invalidated).

        :param encoded_refresh_token: encoded refresh token
        :return: a JwtData containing the new access token, its expiration time,
        a new refresh token and its expiration time
        """

        try:
            old_refresh_token = decode_jwt_refresh_token(encoded_refresh_token)
        except jwt.ExpiredSignatureError:
            raise ExpiredJwtRefreshToken()
        old_jti, profile_id = (old_refresh_token["jti"],
                               old_refresh_token["profile_id"])
        stored_token = await self._repo.find_jwt_refresh_token(old_jti)
        if not stored_token or not stored_token.valid:
            raise InvalidatedJwtRefreshToken()
        new_jwt_data = self._generate_jwt_access_token(
            await self._repo.find_profile_by_id(
                profile_id))
        new_jwt_refresh_data = await self._perform_refresh_token_rotation(
            profile_id=profile_id, previous_token_id=old_jti)
        return JwtData(access_token=new_jwt_data.access_token,
                       access_exp=new_jwt_data.access_exp,
                       refresh_token=new_jwt_refresh_data.refresh_token,
                       refresh_exp=new_jwt_refresh_data.refresh_exp)

    @db.transaction()
    async def _perform_refresh_token_rotation(
            self, profile_id: UUID,
            previous_token_id: UUID) -> JwtRefreshTokenData:
        await self._repo.update_jwt_refresh_token(
            token_id=previous_token_id,
            values=dict(valid=False,
                        invalidated_at=dt.datetime.now(dt.timezone.utc)))
        return await self._generate_jwt_refresh_token(
            profile_id=profile_id, previous_token_id=previous_token_id)

    async def _check_password(self, password: str, password_hash: str) -> bool:
        return await cpu_bound_task(bcrypt.checkpw,
                                    password.encode(), password_hash.encode())

    def _generate_jwt_access_token(self, profile_data: Profile) -> JwtTokenData:
        iat = dt.datetime.now(dt.timezone.utc)
        exp = iat + dt.timedelta(seconds=cfg.jwt_expiration_seconds)
        user_payload = profile_data.dict()
        user_payload["id"] = str(profile_data.id)
        payload = JwtTokenPayload(iat=iat,
                                  exp=exp,
                                  user=JwtUser(**user_payload))
        enc_jwt = jwt.encode(
            payload=payload.dict(),
            key=cfg.jwt_secret,
            algorithm=cfg.jwt_algorithm)
        return JwtTokenData(access_token=enc_jwt,
                            access_exp=timegm(exp.utctimetuple()))

    async def _generate_jwt_refresh_token(
            self,
            profile_id: UUID,
            previous_token_id: Optional[UUID] = None) -> JwtRefreshTokenData:
        token = JwtRefreshToken(
            profile_id=profile_id,
            issued_at=dt.datetime.now(dt.timezone.utc),
            expires_at=dt.datetime.now(dt.timezone.utc) + dt.timedelta(
                seconds=cfg.jwt_refresh_expiration_seconds),
            previous_token_id=previous_token_id)
        token = await self._repo.save_jwt_refresh_token(token)
        enc_jwt_refresh = jwt.encode(
            payload=JwtRefreshTokenPayload(
                iat=token.issued_at,
                exp=token.expires_at,
                jti=str(token.id),
                profile_id=str(profile_id)).dict(),
            key=cfg.jwt_secret,
            algorithm=cfg.jwt_algorithm)
        return JwtRefreshTokenData(
            refresh_token=enc_jwt_refresh,
            refresh_exp=timegm(token.expires_at.utctimetuple()))
