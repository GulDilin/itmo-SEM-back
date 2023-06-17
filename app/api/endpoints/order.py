from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post('/', response_model=schemas.Order)
async def create_order(
        order: schemas.OrderCreate,
        order_service: services.OrderService = Depends(deps.get_order_service),
        order_type_service: services.OrderTypeService = Depends(deps.get_order_type_service),
) -> schemas.Order:
    order_type = await deps.get_path_order_type(
        order_type_id=order.order_type_id,
        order_type_service=order_type_service
    )
    return schemas.Order(**jsonable_encoder(
        await order_service.create(order, order_type=order_type)
    ))


@router.get('/', response_model=schemas.PaginatedResponse)
async def get_orders(
    paginator: schemas.PaginationData = Depends(),
    order_service: services.OrderService = Depends(deps.get_order_service),
    user_data: schemas.User = Depends(deps.get_user_data)
) -> schemas.PaginatedResponse:
    print(user_data)
    return await util.get_paginated_response(
        await order_service.read_many_paginated(
            wrapper_class=schemas.Order,
            offset=paginator.offset,
            limit=paginator.limit,
            load_props=['params.order_type_param'],
        ),
        paginator
    )


@router.get('/{order_id}', response_model=schemas.Order)
async def get_order(
    order: entities.Order = Depends(deps.get_path_order),
) -> schemas.Order:
    return schemas.Order(**jsonable_encoder(order))


@router.put('/{order_id}', response_model=schemas.Order)
async def update_order(
    order_update_data: schemas.OrderUpdate,
    order: entities.Order = Depends(deps.get_path_order),
    order_service: services.OrderService = Depends(deps.get_order_service),
) -> schemas.Order:
    updated = await order_service.update(
        id=str(order.id),
        **jsonable_encoder(order_update_data, exclude_none=True)
    )
    return schemas.Order(**jsonable_encoder(updated))


@router.delete('/{order_id}')
async def delete_order(
    order: entities.Order = Depends(deps.get_path_order),
    order_service: services.OrderService = Depends(deps.get_order_service),
) -> None:
    await order_service.delete(id=order.id)
