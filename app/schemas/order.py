from pydantic import BaseModel

from .util import StrEnum, TimestampedWithId


class OrderStatus(StrEnum):
    NEW = 'NEW'


class OrderCreate(BaseModel):
    user_customer: str
    user_implementer: str


class OrderUpdate(BaseModel):
    status: OrderStatus
    user_customer: str
    user_implementer: str


class Order(TimestampedWithId):
    status: str
    user_customer: str
    user_implementer: str
