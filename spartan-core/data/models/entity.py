from datetime import datetime
from typing import Union

from pydantic import BaseModel


class EntityRead(BaseModel):
    id: str
    correlation_id: Union[str, None] = None
    idea_id: Union[str, None] = None
    file_id: Union[str, None] = None
    value: str
    type: str
    start: Union[int, None] = None
    end: Union[int, None] = None
    unit: Union[int, None] = None
    attributes: Union[dict, None] = None
    created_ts: datetime
    modified_ts: datetime


class EntityUpdate(BaseModel):
    correlation_id: Union[str, None] = None
    idea_id: Union[str, None] = None
    file_id: Union[str, None] = None
    value: str
    type: str
    start: Union[int, None] = None
    end: Union[int, None] = None
    unit: Union[int, None] = None
    attributes: Union[dict, None] = None


class EntityList(BaseModel):
    data: list[EntityRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
    sorting: Union[dict, None] = None
