from typing import List

from pydantic import BaseModel

from .order_type_param import OrderTypeParam
from .util import TimestampedWithId


class OrderTypeCreate(BaseModel):
    name: str


class OrderTypeUpdate(BaseModel):
    name: str


class OrderType(TimestampedWithId):
    name: str
    dep_type: str
    params: List[OrderTypeParam]
