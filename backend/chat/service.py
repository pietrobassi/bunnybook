import asyncio
import datetime as dt
from asyncio import get_event_loop
from typing import Optional, List, Dict, Union
from uuid import UUID

import socketio
from fastapi.encoders import jsonable_encoder
from injector import singleton, inject

from auth.models import User
from chat.models import ChatMessage, Conversation, PrivateChat
from chat.repo import ChatRepo
from chat.schemas import IsTypingWsMessage, ChatMessageRead, PrivateChatRead
from pubsub.websocket import WebSockets, WsRouter, get_sio_session, \
    save_sio_session, SioSession


@singleton
class ChatService(WsRouter):
    @inject
    def __init__(self, repo: ChatRepo, ws: WebSockets):
        self._repo = repo
        self._ws = ws
        self._sio = ws.sio

    async def get_conversation_messages(
            self,
            chat_group_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: Optional[int] = 10) -> List[ChatMessage]:
        """Retrieve conversation messages."""
        return await self._repo.find_chat_group_messages(
            chat_group_id, older_than, limit)

    async def get_conversations(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[Conversation]:
        """Get conversations for a specific profile."""
        return await self._repo.find_conversations_by_profile_id(
            profile_id,
            older_than,
            limit)

    async def get_chat_group_members_profile_ids(self, chat_group_id: UUID) \
            -> List[UUID]:
        """Return ids of a chat group members."""
        return await self._repo.find_chat_group_members_profile_ids(
            chat_group_id)

    async def get_private_chats_by_profile_id(self, profile_id: UUID) \
            -> List[PrivateChat]:
        """Return all private chat groups for a specific profile.."""
        return await self._repo.find_private_chats_by_profile_id(profile_id)

    async def _on_chat_message(self, sid: str, data: Dict):
        message, to = data["message"], UUID(data["to"])
        session = await get_sio_session(sid)
        if to not in [chat.chat_group_id
                      for chat in session.private_chats]:
            return
        chat_message = ChatMessage(
            from_profile_id=session.user.id,
            chat_group_id=to,
            content=message)
        chat_message = await self._repo.save_chat_message(chat_message)
        await self._repo.update_chat_message_read_status(
            session.user.id,
            to,
            chat_message.id)
        message_data = ChatMessageRead(
            id=chat_message.id,
            content=message,
            from_profile_id=session.user.id,
            chat_group_id=chat_message.chat_group_id,
            created_at=chat_message.created_at)
        for recipient in (await self._get_message_recipients(to, sid)):
            await self._ws.send("chat_message", message_data, to=recipient)
        return jsonable_encoder(message_data)

    async def _on_is_typing(self, sid: str, data: Dict):
        chat_group_id = UUID(data["chatGroupId"])
        session = await get_sio_session(sid)
        message_data = IsTypingWsMessage(
            profile_id=session.user.id,
            username=session.user.username,
            chat_group_id=chat_group_id)
        for recipient in (await self._get_message_recipients(
                chat_group_id, sid, exclude_sender_id=session.user.id)):
            await self._ws.send("is_typing", message_data, to=recipient)

    async def _on_mark_chat_as_read(self, sid: str, data: Dict):
        chat_group_id, chat_message_id = data["chatGroupId"], \
                                         data["chatMessageId"]
        session = await get_sio_session(sid)
        await self._repo.update_chat_message_read_status(
            session.user.id,
            chat_group_id,
            chat_message_id)

    async def _get_message_recipients(
            self,
            chat_group_id: UUID,
            sid: Optional[str] = None,
            exclude_sender_id: Optional[Union[str, UUID]] = None,
    ) -> List[str]:
        if sid:
            session = await get_sio_session(sid)
            recipients = [str(private_chat.profile_id)
                          for private_chat in session.private_chats
                          if private_chat.chat_group_id == chat_group_id]
            if not exclude_sender_id:
                recipients.append(sid)
            return recipients
        return [str(profile_id) for profile_id
                in await self._repo.find_chat_group_members_profile_ids(
                chat_group_id)
                if (True if not exclude_sender_id
                    else str(profile_id) != str(exclude_sender_id))]

    async def _on_ws_connect(self, sid: str, user: User):
        private_chats = await self.get_private_chats_by_profile_id(user.id)
        unread_conversations_ids = await \
            self._repo.find_unread_conversations_ids_by_profile_id(user.id)
        await save_sio_session(sid, SioSession(user=user,
                                               private_chats=private_chats))
        await self._ws.send(
            event="unread_conversations_ids",
            payload=unread_conversations_ids,
            to=sid)
        await self._ws.send(
            event="private_chats",
            payload=[PrivateChatRead(**chat.dict()) for chat in private_chats],
            to=sid)
        get_event_loop().create_task(self._online_friends_task(sid))

    async def _online_friends_task(self, sid: str):
        while True:
            try:
                session = await get_sio_session(sid)
            except KeyError:
                return
            friends_uuids = [friend.profile_id
                             for friend in session.private_chats]
            await self._ws.send(
                event="online_friends",
                payload=await self._ws.store.get_online_statuses(friends_uuids),
                to=sid)
            await asyncio.sleep(5)

    def subscribe_to_on_connect(self):
        self._ws.subscribe_to_on_connect(self._on_ws_connect)

    def add_ws_routes(self, sio: socketio.AsyncServer):
        sio.on("chat_message", self._on_chat_message)
        sio.on("is_typing", self._on_is_typing)
        sio.on("mark_chat_as_read", self._on_mark_chat_as_read)
