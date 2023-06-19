from typing import Dict, List, Optional

from pydantic import BaseModel

from .. import schemas
from .order_param_value import OrderParamValue
from .util import StrEnum, TimestampedWithId


class OrderStatus(StrEnum):
    NEW = 'NEW'
    READY = 'READY'
    IN_PROGRESS = 'IN PROGRESS'
    DONE = 'DONE'
    ACCEPTED = 'ACCEPTED'
    TO_REMOVE = 'TO REMOVE'
    REMOVED = 'REMOVED'


class OrderTypeName(StrEnum):
    BATH_ORDER = 'Заказ на баню'
    TIMBER_ORDER = 'Заявка на сруб'
    TIMBER_DEFECT_ORDER = 'Заявка на брак сруба'


order_type_requisites: Dict[str, List[str]] = {
    OrderTypeName.BATH_ORDER: [schemas.UserRole.STAFF_CUSTOMER_MANAGER, schemas.UserRole.STAFF_ORDER_MANAGER, ],
    OrderTypeName.TIMBER_ORDER: [schemas.UserRole.STAFF_ORDER_MANAGER, schemas.UserRole.STAFF_AXEMAN],
    OrderTypeName.TIMBER_DEFECT_ORDER: [schemas.UserRole.STAFF_ORDER_MANAGER],
}

order_status_requisites: Dict[str, List[str]] = {
    OrderStatus.NEW: [schemas.UserRole.STAFF_CUSTOMER_MANAGER],
    OrderStatus.READY: [schemas.UserRole.STAFF_CUSTOMER_MANAGER],
    OrderStatus.IN_PROGRESS: [schemas.UserRole.STAFF_AXEMAN],
    OrderStatus.DONE: [schemas.UserRole.STAFF_AXEMAN],
    OrderStatus.ACCEPTED: [schemas.UserRole.STAFF_ORDER_MANAGER],
}

allowed_status_transitions: Dict[str, List[str]] = {
    OrderStatus.NEW: [OrderStatus.READY],
    OrderStatus.READY: [OrderStatus.NEW, OrderStatus.IN_PROGRESS],
    OrderStatus.IN_PROGRESS: [OrderStatus.DONE],
    OrderStatus.DONE: [OrderStatus.ACCEPTED, OrderStatus.READY],
    OrderStatus.ACCEPTED: [],
    OrderStatus.TO_REMOVE: [OrderStatus.NEW,
                            OrderStatus.READY,
                            OrderStatus.IN_PROGRESS,
                            OrderStatus.DONE,
                            OrderStatus.ACCEPTED,
                            OrderStatus.REMOVED],
    OrderStatus.REMOVED: [OrderStatus.NEW,
                          OrderStatus.READY,
                          OrderStatus.IN_PROGRESS,
                          OrderStatus.DONE,
                          OrderStatus.ACCEPTED],
}


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


def raise_order_type(user: schemas.User, order_type: str) -> None:
    user.check_one_role(order_type_requisites[order_type])


def raise_order_status_update(user: schemas.User, old_status: OrderStatus, new_status: OrderStatus) -> None:
    user.check_one_role(order_status_requisites[new_status])
    if new_status not in allowed_status_transitions[old_status]:
        raise ValueError(f'Could not transition from {old_status} to {new_status}')
