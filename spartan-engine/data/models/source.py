from datetime import datetime
from typing import Union

from pydantic import BaseModel


class IdeaSourceRead(BaseModel):
    id: str
    url: str
    name: Union[str, None] = None
    attributes: Union[dict, None] = None
    created_ts: datetime
    modified_ts: datetime


class IdeaSourceUpdate(BaseModel):
    url: str
    name: Union[str, None] = None
    attributes: Union[dict, None] = None


class IdeaSourceList(BaseModel):
    data: list[IdeaSourceRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
