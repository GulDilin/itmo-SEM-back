from pydantic import BaseModel

from .util import TimestampedWithId


class OrderTypeCreate(BaseModel):
    name: str


class OrderTypeUpdate(BaseModel):
    name: str


class OrderType(TimestampedWithId):
    name: str
