from datetime import datetime
from typing import Union

from pydantic import BaseModel


class FiletRead(BaseModel):
    id: str
    correlation_id: Union[str, None] = None
    idea_id: str
    name: str
    content_type: str
    size: int
    attributes: Union[dict, None] = None
    hash: str
    hash_type: str
    created_ts: datetime
    modified_ts: datetime


class FileUpdate(BaseModel):
    correlation_id: Union[str, None] = None
    attributes: Union[dict, None] = None


class FileList(BaseModel):
    data: list[FiletRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
    sorting: Union[dict, None] = None
