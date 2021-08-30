import hashlib
import json
from functools import wraps
from typing import Any

from fastapi.encoders import jsonable_encoder

from common.log import logger
from config import cfg


def fail_silently(default: Any = None):
    """Cache shouldn't make requests fail if cache backend is unavailable or not
    responding.
    When not in production mode, this decorator is ignored to ease debugging."""

    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except Exception as e:
                if not cfg.prod:
                    raise e
                logger.error("Cache access failed")
                return default

        return wrapper

    return decorator


def hash_cache_key(*args):
    """Generate a key from (hashable) parameters."""
    # cannot use hash(args) since hash function is not stable since Python 3.3
    return hashlib.md5(json.dumps(jsonable_encoder(args)).encode()).hexdigest()
