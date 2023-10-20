from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel


class ReferenceType(str, Enum):
    unlinked = "UNLINKED"
    linked = "LINKED"


class ReferenceUpdate(BaseModel):
    correlation_id: Union[str, None] = None
    source_idea_id: Union[str, None] = None
    target_idea_id: Union[str, None] = None
    type: ReferenceType
    attributes: Union[dict, None] = None


class ReferenceRead(BaseModel):
    id: str
    correlation_id: Union[str, None] = None
    source_idea_id: Union[str, None] = None
    target_idea_id: Union[str, None] = None
    type: ReferenceType
    attributes: Union[dict, None] = None
    created_ts: datetime
    modified_ts: datetime


class ReferenceList(BaseModel):
    data: list[ReferenceRead]
    query: Union[dict, None] = None
    pagination: Union[dict, None] = None
    sorting: Union[dict, None] = None
