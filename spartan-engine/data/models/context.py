from typing import Union

from pydantic import BaseModel


class ContextRead(BaseModel):
    id: str
    count: Union[int, None] = None


class ContextList(BaseModel):
    context: str
    data: list[ContextRead]