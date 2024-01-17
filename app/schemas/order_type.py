from typing import List, Optional

from pydantic import BaseModel

from .order_type_param import OrderTypeParam
from .util import TimestampedWithId


class OrderTypeCreate(BaseModel):
    name: str
    dep_type: str


class OrderTypeUpdate(BaseModel):
    name: str


class OrderType(TimestampedWithId):
    name: str
    dep_type: Optional[str]
    params: List[OrderTypeParam]
