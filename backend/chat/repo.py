import datetime as dt
from typing import Optional, List
from uuid import UUID

import asyncpg
import sqlalchemy
from injector import singleton
from sqlalchemy import insert, select, delete, desc, update

from chat.exceptions import NonExistentChatGroup
from chat.models import ChatMessage, chat_message, chat_group, ChatGroup, \
    profile_chat_group, chat_message_read_status, Conversation, PrivateChat
from common.injection import injector
from database.core import db
from database.utils import map_result


@singleton
class ChatRepo:
    @map_result
    async def save_chat_message(self, new_message: ChatMessage) -> ChatMessage:
        try:
            return await db.fetch_one(
                insert(chat_message)
                    .values(new_message.dict(exclude_none=True))
                    .returning(chat_message))
        except asyncpg.exceptions.ForeignKeyViolationError as e:
            if e.constraint_name == "chat_message_chat_group_id_fkey":
                raise NonExistentChatGroup()
            raise

    @map_result
    @db.transaction()
    async def save_chat_group(
            self,
            profile_ids: List[UUID],
            group_name: Optional[str] = None,
            private: bool = True) -> ChatGroup:
        group = (await db.fetch_one(insert(chat_group).values(
            ChatGroup(name=group_name, private=private).dict(exclude_none=True))
                                    .returning(chat_group)))
        await self.save_chat_group_members(profile_ids, group["id"], private)
        return group

    async def save_chat_group_members(
            self,
            profile_ids: List[UUID],
            chat_group_id: UUID,
            private: bool) -> None:
        query = profile_chat_group.insert()
        if private:
            from profiles.repo import ProfilesRepo
            profiles_repo = injector.get(ProfilesRepo)
            username_first_profile_id = (
                await profiles_repo.find_profile_by_id(profile_ids[0])).username
            username_second_profile_id = (
                await profiles_repo.find_profile_by_id(profile_ids[1])).username
            values = [dict(profile_id=profile_ids[0],
                           chat_group_id=chat_group_id,
                           name=username_second_profile_id),
                      dict(profile_id=profile_ids[1],
                           chat_group_id=chat_group_id,
                           name=username_first_profile_id)]
        else:
            values = [dict(profile_id=profile_id, chat_group_id=chat_group_id)
                      for profile_id in profile_ids]
        await db.execute_many(query=query, values=values)

    async def update_chat_message_read_status(
            self,
            profile_id: UUID,
            chat_group_id: UUID,
            chat_message_id: UUID):
        return await db.fetch_one(
            sqlalchemy.dialects.postgresql.insert(
                chat_message_read_status).values(
                profile_id=profile_id,
                chat_group_id=chat_group_id,
                chat_message_id=chat_message_id,
                read_at=dt.datetime.now(dt.timezone.utc))
                .on_conflict_do_update(
                constraint="profile_id_chat_group_id_idx",
                set_=dict(chat_message_id=chat_message_id,
                          read_at=dt.datetime.now(dt.timezone.utc))))

    @map_result
    async def update_chat_group(self, chat_group_id: UUID, active: bool) \
            -> ChatGroup:
        return await db.fetch_one(update(chat_group)
                                  .where(chat_group.c.id == chat_group_id)
                                  .values(active=active)
                                  .returning(chat_group))

    @map_result
    async def find_conversations_by_profile_id(
            self,
            profile_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[Conversation]:
        older_than = older_than or dt.datetime.now(dt.timezone.utc)
        query = """
        SELECT * FROM (
            SELECT DISTINCT ON (pcg.profile_id, pcg.chat_group_id)
                cm.from_profile_id, cm.content, cm.created_at, p.username from_profile_username, cm.chat_group_id, COALESCE (pcg.name, cg.name) chat_group_name, cmrs.read_at
            FROM chat_message cm
                JOIN profile_chat_group pcg on cm.chat_group_id = pcg.chat_group_id
                JOIN chat_group cg ON cm.chat_group_id = cg.id
                JOIN profile p ON cm.from_profile_id = p.id
                LEFT OUTER JOIN chat_message_read_status cmrs ON cm.id = cmrs.chat_message_id
                    AND cmrs.profile_id = pcg.profile_id
            WHERE pcg.profile_id = :profile_id
                AND cg.active = true
            ORDER BY pcg.profile_id, pcg.chat_group_id, cm.created_at DESC
        ) conversations
        WHERE created_at < :older_than
        ORDER BY created_at DESC
        LIMIT :limit"""
        return await db.fetch_all(
            query=query,
            values=dict(
                profile_id=profile_id, older_than=older_than, limit=limit))

    async def find_unread_conversations_ids_by_profile_id(
            self, profile_id: UUID) -> List[UUID]:
        query = """SELECT chat_group_id FROM (
        SELECT chat_group_id, read_at FROM (
            SELECT DISTINCT ON (pcg.profile_id, pcg.chat_group_id) cmrs.read_at read_at, pcg.chat_group_id chat_group_id
            FROM chat_message cm
                JOIN profile_chat_group pcg ON cm.chat_group_id = pcg.chat_group_id
                JOIN chat_group cg ON cm.chat_group_id = cg.id
                LEFT OUTER JOIN chat_message_read_status cmrs
            ON cm.id = cmrs.chat_message_id AND cmrs.profile_id = pcg.profile_id
            WHERE pcg.profile_id = :profile_id
                AND cg.active = TRUE
            ORDER BY pcg.profile_id, pcg.chat_group_id, cm.created_at DESC
            ) conversations
        WHERE read_at IS NULL) unread_conversations"""
        results = await db.fetch_all(
            query=query,
            values=dict(profile_id=profile_id))
        return [result["chat_group_id"] for result in results]

    @map_result
    async def find_private_chats_by_profile_id(self, profile_id: UUID) \
            -> List[PrivateChat]:
        query = """SELECT cg.id chat_group_id, pcg2.profile_id, p.username
        FROM profile_chat_group pcg1
            JOIN profile_chat_group pcg2 ON pcg1.chat_group_id = pcg2.chat_group_id
            JOIN chat_group cg ON cg.id = pcg2.chat_group_id
            JOIN profile p ON p.id = pcg2.profile_id
        WHERE pcg1.profile_id != pcg2.profile_id
            AND pcg1.profile_id = :profile_id
            AND cg.private = TRUE
            AND cg.active = TRUE"""
        return await db.fetch_all(
            query=query,
            values=dict(profile_id=profile_id))

    async def find_chat_group_members_profile_ids(self, group_id: UUID) \
            -> List[UUID]:
        results = await db.fetch_all(
            select([profile_chat_group.c.profile_id])
                .where(profile_chat_group.c.chat_group_id == group_id))
        return [result["profile_id"] for result in results]

    @map_result
    async def delete_chat_group(self, chat_group_id: UUID) \
            -> Optional[ChatGroup]:
        return await db.fetch_one(delete(chat_group)
                                  .where(chat_group.c.id == chat_group_id)
                                  .returning(chat_group))

    @map_result
    async def find_private_chat_group(
            self, profile_id: UUID, other_profile_id: UUID) \
            -> Optional[ChatGroup]:
        query = """SELECT cg.id, cg.name, cg.private, cg.active
        FROM profile_chat_group pcg1
            JOIN profile_chat_group pcg2 ON pcg1.chat_group_id = pcg2.chat_group_id
            JOIN chat_group cg ON pcg1.chat_group_id = cg.id
        WHERE pcg1.profile_id = :profile_id
            AND pcg2.profile_id = :other_profile_id
            AND cg.private = TRUE"""
        return await db.fetch_one(
            query=query,
            values=dict(profile_id=profile_id,
                        other_profile_id=other_profile_id))

    @map_result
    async def find_chat_group_messages(
            self,
            chat_group_id: UUID,
            older_than: Optional[dt.datetime] = None,
            limit: int = 10) -> List[ChatMessage]:
        older_than = older_than or dt.datetime.now(dt.timezone.utc)
        return await db.fetch_all(
            select([chat_message])
                .where(chat_message.c.chat_group_id == chat_group_id)
                .where(chat_message.c.created_at < older_than)
                .order_by(desc(chat_message.c.created_at))
                .limit(limit))
