from functools import wraps
from typing import get_type_hints, Any, TypeVar, Type, Callable

from pydantic import parse_obj_as
from sqlalchemy import Column, DateTime, text, func
from sqlalchemy.dialects.postgresql import UUID

# PostgreSQL UUID type
PgUUID = UUID(as_uuid=False)

# Generate random UUID primary key column
uuid_pk = lambda: Column("id",
                         PgUUID,
                         primary_key=True,
                         server_default=text("uuid_generate_v4()"))

# Generate created_at column (optionally indexed) with current time as default
created_at = lambda index=False: Column("created_at",
                                        DateTime(timezone=True),
                                        nullable=False,
                                        server_default=func.now(),
                                        index=index)

# Generate updated_at column (optionally indexed) with None as default
updated_at = lambda index=False: Column("updated_at",
                                        DateTime(timezone=True),
                                        default=None,
                                        index=index)

T = TypeVar("T")


def map_to(obj: Any, to_type: Type[T], is_graph_result: bool = False) -> T:
    """
    Convert object to a pydantic BaseModel class.

    :param obj: object to convert
    :param to_type: destination pydantic type
    :param is_graph_result: pass True if obj is a Neo4j query result
    :return: converted object
    """
    if is_graph_result:
        obj = [item[0] for item in obj]
    return parse_obj_as(to_type, obj) if obj else obj


def map_result(function: Callable) -> Callable:
    """Map the Sqlalchemy list result returned by wrapped function to the
    declared return type, which must extend pydantic BaseModel class."""

    @wraps(function)
    async def wrapper(*args, **kwargs):
        return_type = get_type_hints(wrapper).get("return")
        result = await function(*args, **kwargs)
        return parse_obj_as(return_type, result) if return_type and result \
            else result

    return wrapper


def map_graph_result(function: Callable) -> Callable:
    """Map the Neo4j nodes result returned by wrapped function to the declared
    return type, which must extend pydantic BaseModel."""

    @wraps(function)
    async def wrapper(*args, **kwargs):
        return_type = get_type_hints(wrapper).get("return")
        result = await function(*args, **kwargs)
        result = [item[0] for item in result]
        return parse_obj_as(return_type, result) if return_type and result \
            else result

    return wrapper
