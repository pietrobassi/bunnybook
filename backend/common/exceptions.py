from typing import Any, Optional, Dict

from fastapi import HTTPException


class HTTPExceptionJSON(HTTPException):
    """FastAPI HTTPException enriched with 'code' and 'data' fields, useful to
    add some context to the error message."""

    def __init__(self,
                 status_code: int,
                 code: str = None,
                 detail: Any = None,
                 headers: Optional[Dict[str, Any]] = None,
                 data: Dict[str, Any] = None,
                 ) -> None:
        super().__init__(status_code=status_code,
                         detail=detail,
                         headers=headers)
        self.code = code
        self.data = data
