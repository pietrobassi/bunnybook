import sys

from fastapi_limiter.depends import RateLimiter
from starlette.requests import Request
from starlette.responses import Response


class RateLimitTo(RateLimiter):
    """Wrapper over RateLimiter to bypass rate limiting during pytest runs."""

    async def __call__(self, request: Request, response: Response):
        if "pytest" in sys.modules:
            return
        await super().__call__(request, response)
