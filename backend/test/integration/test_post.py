import pytest

from test.integration.utils import remove_friend, become_friends


@pytest.mark.asyncio
async def test_create_post(ben):
    new_post_content = "Test"
    new_post_req = await ben.conn.post("/posts",
                                       json={"content": new_post_content})
    assert new_post_req.status_code == 201
    new_post = new_post_req.json()
    assert new_post["content"] == new_post_content


@pytest.mark.asyncio
async def test_post_privacy(ben, daisy):
    public_post = (await ben.conn.post(
        "/posts",
        json={"content": "public", "privacy": "PUBLIC"})).json()
    friends_post = (await ben.conn.post(
        "/posts",
        json={"content": "friends", "privacy": "FRIENDS"})).json()
    assert ((await ben.conn.get(f"/posts/{public_post['id']}")).status_code,
            (await ben.conn.get(f"/posts/{friends_post['id']}")).status_code) \
           == (200, 200)
    assert ((await daisy.conn.get(f"/posts/{public_post['id']}")).status_code,
            (await daisy.conn.get(f"/posts/{friends_post['id']}")).status_code) \
           == (200, 403)
    await become_friends(ben, daisy)
    assert ((await daisy.conn.get(f"/posts/{public_post['id']}")).status_code,
            (await daisy.conn.get(f"/posts/{friends_post['id']}")).status_code) \
           == (200, 200)
    await remove_friend(ben, daisy)
    assert ((await daisy.conn.get(f"/posts/{public_post['id']}")).status_code,
            (await daisy.conn.get(f"/posts/{friends_post['id']}")).status_code) \
           == (200, 403)


@pytest.mark.asyncio
async def test_get_many_posts(ben, daisy):
    await ben.conn.post("/posts", json={"content": "c", "privacy": "PUBLIC"})
    await ben.conn.post("/posts", json={"content": "c", "privacy": "FRIENDS"})
    posts = (await daisy.conn.get("/posts",
                                  params={"wall_profile_id": ben.id})).json()
    assert len(posts) == 1
    await become_friends(ben, daisy)
    posts = (await daisy.conn.get("/posts",
                                  params={"wall_profile_id": ben.id})).json()
    assert len(posts) == 2


@pytest.mark.asyncio
async def test_post_delete(ben):
    post = await ben.conn.post("/posts", json={"content": "Test"})
    post_id = post.json()["id"]
    assert (await ben.conn.get(f"/posts/{post_id}")).json()["id"] == post_id
    assert (await ben.conn.delete(f"/posts/{post_id}")).status_code == 204
    assert (await ben.conn.get(f"/posts/{post_id}")).status_code == 404
    assert (await ben.conn.delete(f"/posts/{post_id}")).status_code == 404


@pytest.mark.asyncio
async def test_post_delete_from_other_profile(ben, daisy):
    post = await ben.conn.post("/posts", json={"content": "Test"})
    post_id = post.json()["id"]
    assert (await daisy.conn.delete(f"/posts/{post_id}")).status_code == 403
    await become_friends(ben, daisy)
    assert (await daisy.conn.delete(f"/posts/{post_id}")).status_code == 403


@pytest.mark.asyncio
async def test_post_delete_on_another_profile_wall(ben, daisy):
    await become_friends(ben, daisy)
    post_id = (await ben.conn.post(
        "/posts",
        json={"content": "Test", "wall_profile_id": daisy.id})).json()["id"]
    assert (await ben.conn.delete(f"/posts/{post_id}")).status_code == 204
    post_id = (await ben.conn.post(
        "/posts",
        json={"content": "Test", "wall_profile_id": daisy.id})).json()["id"]
    assert (await daisy.conn.delete(f"/posts/{post_id}")).status_code == 204


@pytest.mark.asyncio
async def test_post_privacy_on_another_profile_wall(ben, daisy, sumba, pumba):
    await become_friends(ben, daisy)
    public_post = await ben.conn.post(
        "/posts",
        json={"content": "Test",
              "wall_profile_id": daisy.id,
              "privacy": "PUBLIC"})
    public_post_id = public_post.json()["id"]
    friends_post = await ben.conn.post(
        "/posts",
        json={"content": "Test",
              "wall_profile_id": daisy.id,
              "privacy": "FRIENDS"})
    friends_post_id = friends_post.json()["id"]
    assert (await sumba.conn.get(f"/posts/{public_post_id}")).status_code \
           == 200
    assert (await sumba.conn.get(f"/posts/{friends_post_id}")).status_code \
           == 403
    await become_friends(sumba, ben)
    await become_friends(pumba, daisy)
    assert (await sumba.conn.get(f"/posts/{friends_post_id}")).status_code \
           == 403
    assert (await pumba.conn.get(f"/posts/{friends_post_id}")).status_code \
           == 200
