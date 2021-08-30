import datetime as dt
from typing import List, Optional
from uuid import UUID

from fastapi import Query, Depends, HTTPException
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette import status

from auth.models import User
from auth.security import get_user
from chat.schemas import ChatMessageRead, ConversationRead
from chat.service import ChatService
from common.injection import on
from common.rate_limiter import RateLimitTo

chat_router = InferringRouter()


@cbv(chat_router)
class ChatApi:
    _service: ChatService = Depends(on(ChatService))

    @chat_router.get(
        "/chat/{chat_group_id}/messages",
        response_model=List[ChatMessageRead],
        dependencies=[Depends(RateLimitTo(times=10, seconds=1))])
    async def get_messages(
            self,
            chat_group_id: UUID,
            older_than: Optional[dt.datetime] = Query(None),
            limit: Optional[int] = Query(20, ge=1, le=20),
            user: User = Depends(get_user)):
        """Get messages belonging to a specific chat group."""
        if user.id not in await self._service.get_chat_group_members_profile_ids(
                chat_group_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.get_conversation_messages(
            chat_group_id, older_than=older_than, limit=limit)

    @chat_router.get(
        "/profiles/{profile_id}/conversations",
        response_model=List[ConversationRead],
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_conversations(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = Query(None),
            limit: Optional[int] = Query(10, ge=1, le=20),
            user: User = Depends(get_user)):
        """Return list of conversations with at least one message in which a
        specific profile is involved."""
        if user.id != profile_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return await self._service.get_conversations(
            profile_id, older_than=older_than, limit=limit)
