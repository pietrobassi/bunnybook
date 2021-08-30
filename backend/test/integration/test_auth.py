from uuid import uuid4

import pytest

from test.integration.utils import register_user, do_login, register_random_user


@pytest.mark.asyncio
async def test_register():
    uid = str(uuid4())[:32]
    username, email, password = uid, f"{uid}@bunnybook.com", "testpassword"
    register_reponse = await register_user(username, email, password)
    assert register_reponse.status_code == 201
    user = register_reponse.json()
    assert (user["username"], user["email"]) == (username, email)


@pytest.mark.asyncio
async def test_register_conflicts():
    user, password = await register_random_user()
    assert (await register_user(
        "different_username", user["email"], password)).status_code == 409
    assert (await register_user(
        user["username"], "different@email.com", password)).status_code == 409


@pytest.mark.asyncio
async def test_login():
    user, password = await register_random_user()
    login_response = await do_login(user["email"], password)
    assert login_response.status_code == 200
    assert (await do_login(user["email"], "wrong_password")).status_code == 401


@pytest.mark.asyncio
async def test_login_wrong_credentials():
    user, password = await register_random_user()
    assert (await do_login("wrong@email.com", password)).status_code == 401
    assert (await do_login(user["email"], "wrong_password")).status_code == 401
