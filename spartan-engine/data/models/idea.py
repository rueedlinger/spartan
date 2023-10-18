from typing import Union
from datetime import datetime

from pydantic import BaseModel


class IdeaUpdate(BaseModel):
    name: str
    content: str
    tags: Union[set[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None
    attributes: Union[dict, None] = None


class IdeaPatch(BaseModel):
    name: Union[str, None] = None
    content: Union[str, None] = None
    tags: Union[set[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None
    attributes: Union[dict, None] = None


class IdeaRead(BaseModel):
    id: str
    name: str
    content: str
    tags: Union[list[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None
    hash: str
    hash_type: str
    size: int
    attributes: Union[dict, None] = None
    index_ts: Union[datetime, None] = None
    created_ts: datetime
    modified_ts: datetime


class IdeaList(BaseModel):
    data: list[IdeaRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
    sorting: Union[dict, None] = None
