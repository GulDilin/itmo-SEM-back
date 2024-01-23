from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities
from app.schemas.order import OrderStatus, OrderTypeName

router = APIRouter()
router1 = APIRouter()


@router.post("/{order_type_id}/order/", response_model=schemas.Order)
async def create_order(
    order: schemas.OrderCreate,
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order_service: services.OrderService = Depends(deps.get_order_service),
    user: schemas.User = Depends(
        deps.CurrentUser([schemas.UserRole.STAFF_CUSTOMER_MANAGER])
    ),
) -> schemas.Order:
    schemas.raise_order_type(user=user, order_type=str(order_type.name))
    await schemas.raise_user_customer_data(order)
    await schemas.raise_user_implementer_data(order)
    return schemas.Order(
        **jsonable_encoder(await order_service.create(order, order_type=order_type))
    )


@router.get("/{order_type_id}/order/", response_model=schemas.PaginatedResponse)
@router1.get("/", response_model=schemas.PaginatedResponse)
async def get_orders(
    paginator: schemas.PaginationData = Depends(),
    order_type: Optional[entities.OrderType] = Depends(deps.get_path_order_type),
    order_service: services.OrderService = Depends(deps.get_order_service),
    sorting_list: schemas.SortingList = Depends(deps.get_sorting_list),
    filter_data: dict = Depends(deps.get_order_filter),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.PaginatedResponse:
    if order_type:
        filter_data["order_type_id"] = str(order_type.id)
    if "staff" not in user_data.roles:
        filter_data["user_customer"] = str(user_data.user_id)
    return await util.get_paginated_response(
        await order_service.read_many_paginated(
            wrapper_class=schemas.Order,
            offset=paginator.offset,
            limit=paginator.limit,
            sorting_list=sorting_list,
            **filter_data,
        ),
        paginator,
    )


@router.get("/{order_type_id}/test-order/", response_model=schemas.PaginatedResponse)
async def test_get_orders(
    order_type: Optional[entities.OrderType] = Depends(deps.get_path_order_type),
    order_service: services.OrderService = Depends(deps.get_order_service),
    sorting_list: schemas.SortingList = Depends(deps.get_sorting_list),
    filter_data: dict = Depends(deps.get_order_filter),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.PaginatedResponse:
    if order_type:
        filter_data["order_type_id"] = str(order_type.id)
    if "staff" not in user_data.roles:
        filter_data["user_customer"] = str(user_data.user_id)

    return await order_service.read_many_paginated(
        wrapper_class=schemas.Order,
        sorting_list=sorting_list,
        **filter_data,
    )


@router.get("/{order_type_id}/order/{order_id}/", response_model=schemas.Order)
@router1.get("/{order_id}/", response_model=schemas.Order)
async def get_order(
    order: entities.Order = Depends(deps.get_path_order),
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.Order:
    if order.order_type.name != OrderTypeName.BATH_ORDER:
        user_data.check_one_role([schemas.UserRole.STAFF])
    return schemas.Order(**jsonable_encoder(order))


@router.put("/{order_type_id}/order/{order_id}/", response_model=schemas.Order)
async def update_order(
    order_update_data: schemas.OrderUpdate,
    order: entities.Order = Depends(deps.get_path_order),
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order_type_service: services.OrderTypeService = Depends(
        deps.get_order_type_service
    ),
    order_service: services.OrderService = Depends(deps.get_order_service),
    status_service: services.OrderStatusUpdateService = Depends(
        deps.get_update_status_service
    ),
    user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF])),
) -> schemas.Order:
    schemas.raise_order_type(user, str(order_type.name))
    await schemas.raise_user_customer_update_data(order_update_data)
    await schemas.raise_user_implementer_update_data(order_update_data)
    if order_update_data.status is not None:
        schemas.raise_order_type(user=user, order_type=str(order_type.name))
        schemas.raise_order_status_update(
            user=user,
            old_status=schemas.OrderStatus(order.status),
            new_status=order_update_data.status,
        )
        schemas.raise_ready_order_update(
            new_status=order_update_data.status, order=order
        )
        schemas.raise_accepted_order_update(
            new_status=order_update_data.status,
            child_orders=await order_service.read_many(parent_order_id=order.id),
        )
        await status_service.create(
            user=user,
            new_order_status=order_update_data.status,
            old_order_status=schemas.OrderStatus(order.status),
            order_id=str(order.id),
        )
    updated = await order_service.update(
        id=str(order.id), **jsonable_encoder(order_update_data, exclude_none=True)
    )
    return schemas.Order(**jsonable_encoder(updated))


@router.delete("/{order_type_id}/order/{order_id}/")
async def delete_order(
    order: entities.Order = Depends(deps.get_path_order),
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order_service: services.OrderService = Depends(deps.get_order_service),
    status_service: services.OrderStatusUpdateService = Depends(
        deps.get_update_status_service
    ),
    user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF])),
) -> schemas.Order:
    schemas.raise_order_type(user, str(order_type.name))

    schemas.raise_order_status_update(
        user=user,
        old_status=schemas.OrderStatus(order.status),
        new_status=OrderStatus.TO_REMOVE,
    )
    await status_service.create(
        user=user,
        new_order_status=OrderStatus.TO_REMOVE,
        old_order_status=schemas.OrderStatus(order.status),
        order_id=str(order.id),
    )
    updated = await order_service.update(
        id=str(order.id),
        **jsonable_encoder(
            schemas.OrderUpdate(status=OrderStatus.TO_REMOVE), exclude_none=True
        ),
    )
    return schemas.Order(**jsonable_encoder(updated))
