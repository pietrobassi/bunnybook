import pytest

from test.integration.utils import send_friendship_request, get_relationship, \
    cancel_outgoing_friend_request, accept_friendship_request, remove_friend, \
    reject_friendship_request, get_friends, become_friends, get_mutual_friends, \
    get_friend_suggestions


@pytest.mark.asyncio
async def test_friendship_accepted(ben, daisy):
    assert len(await get_friends(ben.id, ben.conn)) \
           == len(await get_friends(daisy.id, daisy.conn)) \
           == 0
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(daisy.id, ben.id, daisy.conn) \
           == "NONE"
    await send_friendship_request(ben.id, daisy.id, ben.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == "OUTGOING_FRIEND_REQUEST"
    assert await get_relationship(daisy.id, ben.id, daisy.conn) \
           == "INCOMING_FRIEND_REQUEST"
    assert len(await get_friends(ben.id, ben.conn)) \
           == len(await get_friends(daisy.id, daisy.conn)) \
           == 0
    await accept_friendship_request(daisy.id, ben.id, daisy.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(daisy.id, ben.id, daisy.conn) \
           == "FRIEND"
    assert len(await get_friends(ben.id, ben.conn)) \
           == len(await get_friends(daisy.id, daisy.conn)) \
           == 1


@pytest.mark.asyncio
async def test_friendship_rejected(ben, daisy):
    await send_friendship_request(ben.id, daisy.id, ben.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == "OUTGOING_FRIEND_REQUEST"
    await reject_friendship_request(daisy.id, ben.id, daisy.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(ben.id, daisy.id, ben.conn) \
           == "NONE"


@pytest.mark.asyncio
async def test_remove_friend(ben, daisy):
    await become_friends(ben, daisy)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(ben.id, daisy.id, ben.conn) \
           == "FRIEND"
    await remove_friend(daisy, ben)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(ben.id, daisy.id, ben.conn) \
           == "NONE"


@pytest.mark.asyncio
async def test_cancel_outgoing_friendship_request(ben, daisy):
    await send_friendship_request(ben.id, daisy.id, ben.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == "OUTGOING_FRIEND_REQUEST"
    await cancel_outgoing_friend_request(ben.id, daisy.id, ben.conn)
    assert await get_relationship(ben.id, daisy.id, ben.conn) \
           == await get_relationship(ben.id, daisy.id, ben.conn) \
           == "NONE"


@pytest.mark.asyncio
async def test_mutual_friends(ben, daisy, sumba, pumba, exempel):
    await become_friends(ben, daisy)
    ben_daisy_friends = await get_mutual_friends(ben.id, daisy.id, ben.conn)
    assert len(ben_daisy_friends) == 0
    await become_friends(ben, sumba)
    await become_friends(daisy, sumba)
    ben_daisy_friends = await get_mutual_friends(ben.id, daisy.id, ben.conn)
    assert len(ben_daisy_friends) == 1
    assert ben_daisy_friends[0]["id"] == sumba.id
    await become_friends(ben, pumba)
    await become_friends(daisy, pumba)
    await become_friends(ben, exempel)
    await become_friends(daisy, exempel)
    ben_daisy_friends = await get_mutual_friends(ben.id, daisy.id, ben.conn)
    assert len(ben_daisy_friends) == 3
    # test lexicographic order
    assert ben_daisy_friends[0]["username"] \
           < ben_daisy_friends[1]["username"] \
           < ben_daisy_friends[2]["username"]


@pytest.mark.asyncio
async def test_friend_suggestions(ben, daisy, sumba, pumba, exempel):
    assert len(await get_friend_suggestions(ben.id, ben.conn)) == 0
    await become_friends(ben, daisy)
    assert len(await get_friend_suggestions(ben.id, ben.conn)) == 0
    await become_friends(daisy, sumba)
    suggestions = await get_friend_suggestions(ben.id, ben.conn)
    assert len(suggestions) == 1
    assert suggestions[0]["id"] == sumba.id
    await become_friends(daisy, pumba)
    await become_friends(daisy, exempel)
    suggestions = await get_friend_suggestions(ben.id, ben.conn)
    assert len(suggestions) == 3
    # test lexicographic order
    assert suggestions[0]["username"] \
           < suggestions[1]["username"] \
           < suggestions[2]["username"]
    await become_friends(ben, sumba)
    assert len(await get_friend_suggestions(ben.id, ben.conn)) == 2
    await remove_friend(ben, daisy)
    assert len(await get_friend_suggestions(ben.id, ben.conn)) == 1
    await remove_friend(ben, sumba)
    assert len(await get_friend_suggestions(ben.id, ben.conn)) == 0
