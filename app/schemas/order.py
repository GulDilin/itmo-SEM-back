from typing import List, Optional

from pydantic import BaseModel

from .order_param_value import OrderParamValue
from .util import StrEnum, TimestampedWithId


class OrderStatus(StrEnum):
    NEW = 'NEW'
    READY = 'READY'
    IN_PROGRESS = 'IN PROGRESS'
    DONE = 'DONE'
    ACCEPTED = 'ACCEPTED'


class CreateOrderStatus(BaseModel):
    new_order_status: OrderStatus
    order_id: str
    order_type_id: str


class OrderStatusUpdate(BaseModel):
    user: str
    old_status: OrderStatus
    new_status: OrderStatus


class OrderCreate(BaseModel):
    user_customer: str
    user_implementer: str
    order_type_id: str
    parent_order_id: Optional[str] = None


class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    user_customer: Optional[str] = None
    user_implementer: Optional[str] = None
    parent_order_id: Optional[str] = None


class Order(TimestampedWithId):
    status: str
    user_customer: str
    user_implementer: str
    order_type_id: Optional[str]
    parent_order_id: Optional[str] = None
    params: List[OrderParamValue]
    history: List[OrderStatusUpdate]
