from datetime import datetime
from typing import Union

from pydantic import BaseModel


class FiletRead(BaseModel):
    id: str
    name: str
    attributes: Union[dict, None] = None
    hash: Union[str, None] = None
    hash_type: Union[str, None] = None
    created_ts: datetime
    modified_ts: datetime


class FileUpdate(BaseModel):
    name: str
    attributes: Union[dict, None] = None
    hash: Union[str, None] = None
    hash_type: Union[str, None] = None


class FileList(BaseModel):
    data: list[FiletRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
