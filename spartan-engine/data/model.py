from datetime import datetime
from enum import Enum
from typing import Union, Dict, Any, Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, GetJsonSchemaHandler, BaseConfig, AfterValidator


class Root(BaseModel):
    version: Union[str, None] = None
    docs: Union[str, None] = None
    redoc: Union[str, None] = None


class ErrorResponseMessage(BaseModel):
    error: str
    message: str
    detail: Union[str, None] = None


class ContextRead(BaseModel):
    id: str
    count: Union[int, None] = None


class ContextList(BaseModel):
    context: str
    data: list[ContextRead]


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
    tags: Union[set[str], None] = None
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


class IdeaReferenceType(str, Enum):
    unlinked = "UNLINKED"
    linked = "LINKED"


class IdeaReferenceUpdate(BaseModel):
    idea_id: str
    name: str
    type: IdeaReferenceType


class IdeaReferenceRead(BaseModel):
    id: str
    idea_id: str
    name: str
    type: IdeaReferenceType
    created_ts: datetime
    modified_ts: datetime


class IdeaReferenceList(BaseModel):
    data: list[IdeaReferenceRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None


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


class EntityRead(BaseModel):
    id: str
    idea_id: Union[str, None] = None
    media_id: Union[str, None] = None
    value: str
    type: str
    start: Union[int, None] = None
    end: Union[int, None] = None
    attributes: Union[dict, None] = None
    created_ts: datetime
    modified_ts: datetime


class EntityUpdate(BaseModel):
    idea_id: Union[str, None] = None
    media_id: Union[str, None] = None
    value: str
    type: str
    start: Union[int, None] = None
    end: Union[int, None] = None
    attributes: Union[dict, None] = None


class EntityList(BaseModel):
    data: list[EntityRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None


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


class MediaRead(BaseModel):
    id: str
    name: str
    attributes: Union[dict, None] = None
    hash: Union[str, None] = None
    hash_type: Union[str, None] = None
    created_ts: datetime
    modified_ts: datetime


class MediaUpdate(BaseModel):
    name: str
    attributes: Union[dict, None] = None
    hash: Union[str, None] = None
    hash_type: Union[str, None] = None


class MediaList(BaseModel):
    data: list[MediaRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None


def convert_doc_value(doc):
    data = {}
    for k, v in doc.items():
        if k == '_id':
            data['id'] = str(v)
        elif isinstance(v, ObjectId):
            data[k] = str(v)
        elif isinstance(v, str) or isinstance(v, int) or isinstance(v, datetime):
            data[k] = v
        else:
            data[k] = v
    return data
