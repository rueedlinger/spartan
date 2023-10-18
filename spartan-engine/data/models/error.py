from typing import Union
from pydantic import BaseModel


class ErrorResponseMessage(BaseModel):
    error: str
    message: str
    detail: Union[str, None] = None
