from datetime import datetime
from typing import Union

from pydantic import BaseModel

class Root(BaseModel):
    version: str




class Detail(BaseModel):
    msg: str
    type: str

class Message(BaseModel):
    message: str
    detail: Union[Detail, None] = None


class IdeaUpdatable(BaseModel):
    name: str
    content: str
    tags: Union[set[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None


class IdeaRead(BaseModel):
    id: str
    name: str
    content: Union[str, None] = None
    tags: Union[set[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None
    hash: str
    hash_type: str
    type: str
    size: int
    created_ts: datetime
    modified_ts: datetime
