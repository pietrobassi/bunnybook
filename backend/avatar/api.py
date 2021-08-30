import io

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from starlette.responses import StreamingResponse

from avatar.service import AvatarService
from common.injection import on
from common.rate_limiter import RateLimitTo

avatar_router = InferringRouter()


@cbv(avatar_router)
class AvatarApi:
    _service: AvatarService = Depends(on(AvatarService))

    @avatar_router.get(
        "/avatar/{identifier}",
        dependencies=[Depends(RateLimitTo(times=5, seconds=1))])
    async def get_random_avatar(self, identifier: str):
        """Get a random generated avatar, using identifier as seed."""
        random_avatar = await self._service.generate_avatar(identifier)
        buffer = io.BytesIO()
        random_avatar.save(buffer, "PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")
