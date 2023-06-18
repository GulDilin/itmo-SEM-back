from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post('/{order_type_id}/order/', response_model=schemas.Order)
async def create_order(
        order: schemas.OrderCreate,
        order_type: entities.OrderType = Depends(deps.get_path_order_type),
        order_service: services.OrderService = Depends(deps.get_order_service),
        user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF]))
) -> schemas.Order:
    # TODO проверить роль пользователя и тип создаваемого order
    return schemas.Order(**jsonable_encoder(
        await order_service.create(order, order_type=order_type)
    ))


@router.get('/{order_type_id}/order/', response_model=schemas.PaginatedResponse)
async def get_orders(
        paginator: schemas.PaginationData = Depends(),
        order_type: entities.OrderType = Depends(deps.get_path_order_type),
        order_service: services.OrderService = Depends(deps.get_order_service),
        user_data: schemas.User = Depends(deps.get_user_data)
) -> schemas.PaginatedResponse:
    print(user_data)
    return await util.get_paginated_response(
        await order_service.read_many_paginated(
            wrapper_class=schemas.Order,
            offset=paginator.offset,
            limit=paginator.limit,
            order_type_id=str(order_type.id),
            load_props=['params.order_type_param'],
        ),
        paginator
    )


@router.get('/{order_type_id}/order/{order_id}', response_model=schemas.Order)
async def get_order(
        order: entities.Order = Depends(deps.get_path_order),
        user_data: schemas.User = Depends(deps.get_user_data)
) -> schemas.Order:
    return schemas.Order(**jsonable_encoder(order))


@router.put('/{order_type_id}/order/{order_id}', response_model=schemas.Order)
async def update_order(
        order_update_data: schemas.OrderUpdate,
        order: entities.Order = Depends(deps.get_path_order),
        order_service: services.OrderService = Depends(deps.get_order_service),
        user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF]))
) -> schemas.Order:
    updated = await order_service.update(
        id=str(order.id),
        **jsonable_encoder(order_update_data, exclude_none=True)
    )
    return schemas.Order(**jsonable_encoder(updated))


@router.delete('/{order_type_id}/order/{order_id}')
async def delete_order(
        order: entities.Order = Depends(deps.get_path_order),
        order_service: services.OrderService = Depends(deps.get_order_service),
        user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF]))
) -> None:
    await order_service.delete(id=order.id)
