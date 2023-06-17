from pydantic import BaseModel

from .util import TimestampedWithId
from .order_type_param import OrderTypeParam
from typing import List

class OrderTypeCreate(BaseModel):
    name: str


class OrderTypeUpdate(BaseModel):
    name: str


class OrderType(TimestampedWithId):
    name: str
    params: List[OrderTypeParam]
