from datetime import datetime
from typing import Union

from pydantic import BaseModel


class ChangeEvent(BaseModel):
    id: Union[str, None] = None
    context: Union[str, None] = None
    type: Union[str, None] = None
    data: Union[dict, None] = None
    created_ts: Union[datetime, None] = None
