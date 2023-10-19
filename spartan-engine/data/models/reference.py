from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel


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
    sorting: Union[dict, None] = None
