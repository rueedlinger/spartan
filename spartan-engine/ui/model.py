from datetime import datetime
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


class IdeaPatch(BaseModel):
    name: Union[str, None] = None
    content: Union[str, None] = None
    tags: Union[set[str], None] = None
    project: Union[str, None] = None
    area: Union[str, None] = None
    resource: Union[str, None] = None
    archive: Union[str, None] = None


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
    index_ts: Union[datetime, None] = None
    created_ts: datetime
    modified_ts: datetime


class IdeaList(BaseModel):
    query: Union[dict, None] = None
    data: list[IdeaRead]


class Pagination(BaseModel):
    total_records: int
    current_page: int
    total_pages: int
    next_page: Union[int, None] = None
    prev_page: Union[int, None] = None


def convert_doc_value(doc):
    data = {}
    for k, v in doc.items():
        if k == '_id':
            data['id'] = str(v)
        elif isinstance(v, str) or isinstance(v, int) or isinstance(v, datetime):
            data[k] = v
        else:
            data[k] = v
    return data