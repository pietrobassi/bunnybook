from typing import Dict, Tuple
from uuid import uuid4

from httpx import AsyncClient

from conftest import app_base_url, TestUser
from main import app


async def get_friends(profile_id: str, conn: AsyncClient) -> Dict:
    return (await conn.get(f"/profiles/{profile_id}/friends")).json()


async def get_mutual_friends(profile_id: str, other_profile_id: str,
                             conn: AsyncClient) -> Dict:
    return (await conn.get(f"/profiles/{profile_id}/"
                           f"friends/{other_profile_id}/mutual_friends")).json()


async def get_friend_suggestions(profile_id: str, conn: AsyncClient) -> Dict:
    return (await conn.get(f"/profiles/{profile_id}/friend_suggestions")).json()


async def get_relationship(profile_id: str,
                           other_profile_id: str,
                           conn: AsyncClient) -> Dict:
    return (await conn.get(
        f"/profiles/{profile_id}/relationships/{other_profile_id}")) \
        .json()


async def send_friendship_request(profile_id: str,
                                  other_profile_id: str,
                                  conn: AsyncClient) -> Dict:
    return (await conn.post(f"/profiles/{profile_id}/"
                            f"outgoing_friend_requests/{other_profile_id}")) \
        .json()


async def accept_friendship_request(profile_id: str,
                                    other_profile_id: str,
                                    conn: AsyncClient) -> Dict:
    return (await conn.post(f"/profiles/{profile_id}/"
                            f"friends/{other_profile_id}")).json()


async def reject_friendship_request(profile_id: str,
                                    requester_profile_id: str,
                                    conn: AsyncClient) -> Dict:
    return (await conn.delete(f"/profiles/{profile_id}/"
                              f"incoming_friend_requests/"
                              f"{requester_profile_id}")).json()


async def cancel_outgoing_friend_request(profile_id: str,
                                         target_profile_id: str,
                                         conn: AsyncClient) -> Dict:
    return (await conn.delete(
        f"/profiles/{profile_id}/"
        f"outgoing_friend_requests/{target_profile_id}")).json()


async def remove_friend(profile: TestUser, friend_profile: TestUser) -> Dict:
    return (await profile.conn.delete(f"/profiles/{profile.id}/"
                                      f"friends/{friend_profile.id}")).json()


async def become_friends(profile: TestUser, other_profile: TestUser):
    await send_friendship_request(
        other_profile.id, profile.id, other_profile.conn)
    await accept_friendship_request(
        profile.id, other_profile.id, profile.conn)


async def register_user(username: str, email: str, password: str):
    async with AsyncClient(app=app,
                           base_url=app_base_url) as conn:
        return await conn.post("/register", json=dict(
            username=username,
            email=email,
            password=password))


async def register_random_user() -> Tuple[Dict, str]:
    uid = str(uuid4())[:32]
    username, email, password = uid, f"{uid}@bunnybook.com", "testpassword"
    return (await register_user(username, email, password)).json(), password


async def do_login(email: str, password: str):
    async with AsyncClient(app=app,
                           base_url=app_base_url) as conn:
        return await conn.post("/login", json=dict(
            email=email,
            password=password))
