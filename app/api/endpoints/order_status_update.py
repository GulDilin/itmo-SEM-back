from typing import Dict, List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps

router = APIRouter()

order_status_requisites: Dict[str, List[str]] = {
    schemas.OrderStatus.NEW: [schemas.UserRole.STAFF_CUSTOMER_MANAGER],
    schemas.OrderStatus.READY: [schemas.UserRole.STAFF_CUSTOMER_MANAGER],
    # TODO move to type check later
    schemas.OrderStatus.IN_PROGRESS: [schemas.UserRole.STAFF_AXEMAN],
    schemas.OrderStatus.DONE: [schemas.UserRole.STAFF_AXEMAN],
    schemas.OrderStatus.ACCEPTED: [schemas.UserRole.STAFF_ORDER_MANAGER],
}


@router.post('/', response_model=schemas.Order)
async def update_order_status(
        order_update: schemas.CreateOrderStatus,
        status_service: services.OrderStatusUpdateService = Depends(deps.get_update_status_service),
        order_service: services.OrderService = Depends(deps.get_order_service),
        user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF]))
) -> schemas.Order:
    user.check_one_role(order_status_requisites[order_update.new_order_status])
    order = await order_service.read_one(id=order_update.order_id, order_type_id=order_update.order_type_id)
    await status_service.create(
        user=user,
        new_order_status=order_update.new_order_status,
        old_order_status=schemas.OrderStatus(order.status),
        order_id=order.id)
    new_order = await order_service.update(
        id=order.id, **jsonable_encoder(schemas.OrderUpdate(
            status=order_update.new_order_status,
            user_customer=order.user_customer,
            user_implementer=order.user_implementer,
            parent_order_id=order.parent_order_id), exclude_none=True))
    return schemas.Order(**jsonable_encoder(new_order))
