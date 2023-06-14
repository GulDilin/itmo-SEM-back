from typing import Optional

from pydantic import BaseModel

from .util import StrEnum, TimestampedWithId


class OrderStatus(StrEnum):
    NEW = 'NEW'


class OrderCreate(BaseModel):
    user_customer: str
    user_implementer: str
    order_type_id: str


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    user_customer: Optional[str] = None
    user_implementer: Optional[str] = None


class Order(TimestampedWithId):
    status: str
    user_customer: str
    user_implementer: str
    order_type_id: Optional[str]