from typing import Union
from datetime import datetime

from pydantic import BaseModel


class LabelRead(BaseModel):
    id: str
    idea_id: Union[str, None] = None
    media_id: Union[str, None] = None
    value: str
    type: str
    attributes: Union[dict, None] = None
    created_ts: datetime
    modified_ts: datetime


class LabelUpdate(BaseModel):
    idea_id: Union[str, None] = None
    media_id: Union[str, None] = None
    value: str
    type: str
    attributes: Union[dict, None] = None


class LabelList(BaseModel):
    data: list[LabelRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
