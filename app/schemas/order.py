from typing import Dict, List, Optional, Sequence

from pydantic import BaseModel

from app.log import logger

from ..db import entities
from .keycloak_user import User, UserRole
from .order_param_value import OrderParamValue
from .order_type import OrderType
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
    DEFECT_ORDER = 'Заявка на брак'


order_type_requisites: Dict[str, List[str]] = {
    OrderTypeName.BATH_ORDER: [UserRole.STAFF_CUSTOMER_MANAGER, UserRole.STAFF_ORDER_MANAGER, ],
    OrderTypeName.TIMBER_ORDER: [UserRole.STAFF_CUSTOMER_MANAGER, UserRole.STAFF_ORDER_MANAGER, UserRole.STAFF_AXEMAN],
    OrderTypeName.DEFECT_ORDER: [UserRole.STAFF_ORDER_MANAGER],
}

order_status_requisites: Dict[str, List[str]] = {
    OrderStatus.NEW: [UserRole.STAFF_CUSTOMER_MANAGER],
    OrderStatus.READY: [UserRole.STAFF_ORDER_MANAGER, UserRole.STAFF_CUSTOMER_MANAGER],
    OrderStatus.IN_PROGRESS: [UserRole.STAFF_AXEMAN, UserRole.STAFF_ORDER_MANAGER],
    OrderStatus.DONE: [UserRole.STAFF_AXEMAN, UserRole.STAFF_ORDER_MANAGER],
    OrderStatus.ACCEPTED: [UserRole.STAFF_ORDER_MANAGER,],
    OrderStatus.TO_REMOVE: [UserRole.STAFF_ORDER_MANAGER, UserRole.STAFF_CUSTOMER_MANAGER],
    OrderStatus.REMOVED: [],
}

allowed_status_transitions: Dict[str, List[str]] = {
    OrderStatus.NEW: [OrderStatus.READY, OrderStatus.TO_REMOVE],
    OrderStatus.READY: [OrderStatus.NEW, OrderStatus.IN_PROGRESS, OrderStatus.TO_REMOVE],
    OrderStatus.IN_PROGRESS: [OrderStatus.DONE, OrderStatus.TO_REMOVE],
    OrderStatus.DONE: [OrderStatus.ACCEPTED, OrderStatus.READY, OrderStatus.TO_REMOVE],
    OrderStatus.ACCEPTED: [OrderStatus.TO_REMOVE],
    OrderStatus.TO_REMOVE: [
        OrderStatus.NEW,
        OrderStatus.READY,
        OrderStatus.IN_PROGRESS,
        OrderStatus.DONE,
        OrderStatus.ACCEPTED,
        OrderStatus.REMOVED,
    ],
    OrderStatus.REMOVED: [
        OrderStatus.NEW,
        OrderStatus.READY,
        OrderStatus.IN_PROGRESS,
        OrderStatus.DONE,
        OrderStatus.ACCEPTED
    ],
}


class CreateOrderStatus(BaseModel):
    new_order_status: OrderStatus
    order_id: str
    order_type_id: str


class OrderStatusUpdate(TimestampedWithId):
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
    parent_order: Optional['Order'] = None
    params: List[OrderParamValue]
    history: List[OrderStatusUpdate]
    order_type: Optional[OrderType]


class OrderFilter(BaseModel):
    id: Optional[List[str]]
    parent_order_id: Optional[List[str]]
    user_customer: Optional[List[str]]
    user_implementer: Optional[List[str]]
    dep_type: Optional[List[str]]
    status: Optional[List[str]]


class OrderDepType(StrEnum):
    MAIN = 'MAIN'
    OPTIONAL = 'OPTIONAL'
    DEPEND = 'DEPEND'
    DEFECT = 'DEFECT'


def raise_order_type(user: User, order_type: str) -> None:
    user.check_one_role(order_type_requisites[order_type])


def raise_order_status_update(user: User, old_status: OrderStatus, new_status: OrderStatus) -> None:
    user.check_one_role(order_status_requisites[new_status])
    if new_status not in allowed_status_transitions[old_status]:
        raise ValueError(f'Could not transition from {old_status} to {new_status}')


def raise_ready_order_update(new_status: OrderStatus, order: entities.Order) -> None:
    if new_status != OrderStatus.READY:
        return
    errors = ''
    order_params_types = {}
    for order_param in order.params:
        order_params_types[order_param.order_type_param_id] = order_param.value
    for param in order.order_type.params:
        if param.required and (param.id not in order_params_types.keys() or order_params_types[param.id] is None):
            errors += f'Param {param.name} should be set\n'
    if len(errors) > 0:
        raise ValueError(errors)


def raise_accepted_order_update(
    new_status: OrderStatus,
    child_orders: Sequence[entities.Order]
) -> None:
    if new_status != OrderStatus.ACCEPTED:
        return
    logger.info(child_orders)
    for child_order in child_orders:
        if child_order.status != OrderStatus.ACCEPTED:
            raise ValueError('Все дочерние заказы должны быть завершены')


async def raise_user_customer_data(
        order_create_data: OrderCreate,
) -> None:
    from ..core import keycloak
    kc = keycloak.get_service_client()
    await kc.get_user_by_id(order_create_data.user_customer)


async def raise_user_implementer_data(
        order_create_data: OrderCreate,
) -> None:
    from ..core import keycloak
    kc = keycloak.get_service_client()
    await kc.get_user_by_id(order_create_data.user_implementer)


async def raise_user_customer_update_data(
        order_update_data: OrderUpdate,
) -> None:
    if order_update_data.user_customer is None:
        return
    from ..core import keycloak
    kc = keycloak.get_service_client()
    await kc.get_user_by_id(order_update_data.user_customer)


async def raise_user_implementer_update_data(
        order_update_data: OrderUpdate,
) -> None:
    if order_update_data.user_implementer is None:
        return
    from ..core import keycloak
    kc = keycloak.get_service_client()
    await kc.get_user_by_id(order_update_data.user_implementer)
