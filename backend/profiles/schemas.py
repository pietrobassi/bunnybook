from uuid import UUID

from common.schemas import BaseSchema


class ProfileRead(BaseSchema):
    id: UUID
    username: str
