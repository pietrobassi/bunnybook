import pytest


@pytest.mark.asyncio
async def test_create_comment(ben):
    content = "Test"
    post_id = (await ben.conn.post("/posts", json={"content": content})) \
        .json()["id"]
    new_comment_request = await ben.conn.post(f"/posts/{post_id}/comments",
                                              json={"content": "Test"})
    assert new_comment_request.status_code == 201
    new_comment = new_comment_request.json()
    assert new_comment["content"] == content
    comments_request = await ben.conn.get(f"/posts/{post_id}/comments")
    assert comments_request.status_code == 200
