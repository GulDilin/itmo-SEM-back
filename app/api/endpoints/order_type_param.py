from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post('/{order_type_id}/params/', response_model=schemas.OrderTypeParam)
async def create_order_type(
        item: schemas.OrderTypeParamCreate,
        order_type: entities.OrderType = Depends(deps.get_path_order_type),
        order_type_param_service: services.OrderTypeParamService = Depends(deps.get_order_type_param_service),
) -> schemas.OrderTypeParam:
    return schemas.OrderTypeParam(**jsonable_encoder(
        await order_type_param_service.create(item=item, order_type=order_type)
    ))


@router.get('/{order_type_id}/params/', response_model=schemas.PaginatedResponse)
async def get_orders(
        paginator: schemas.PaginationData = Depends(),
        order_type: entities.OrderType = Depends(deps.get_path_order_type),
        order_type_param_service: services.OrderTypeParamService = Depends(deps.get_order_type_param_service),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await order_type_param_service.read_many_paginated(
            wrapper_class=schemas.OrderTypeParam,
            order_type_id=order_type.id,
            offset=paginator.offset,
            limit=paginator.limit,
        ),
        paginator
    )


@router.get('/{order_type_id}/params/{order_type_param_id}/', response_model=schemas.OrderTypeParam)
async def get_order_type_param(
        order_type_param: entities.OrderTypeParam = Depends(deps.get_path_order_type_param),
) -> schemas.OrderTypeParam:
    return schemas.OrderTypeParam(**jsonable_encoder(order_type_param))


@router.put('/{order_type_id}/params/{order_type_param_id}/', response_model=schemas.OrderTypeParam)
async def update_order_type_param(
        update_data: schemas.OrderTypeParamUpdate,
        order_type_param: entities.OrderTypeParam = Depends(deps.get_path_order_type_param),
        order_type_param_service: services.OrderTypeParamService = Depends(deps.get_order_type_param_service),
) -> schemas.OrderTypeParam:
    updated = await order_type_param_service.update(
        id=str(order_type_param.id),
        **jsonable_encoder(update_data, exclude_none=True)
    )
    return schemas.OrderTypeParam(**jsonable_encoder(updated))


@router.delete('/{order_type_id}/params/{order_type_param_id}/')
async def delete_order_type_param(
        order_type_param: entities.OrderTypeParam = Depends(deps.get_path_order_type_param),
        order_type_param_service: services.OrderTypeParamService = Depends(deps.get_order_type_param_service),
) -> None:
    await order_type_param_service.delete(id=order_type_param.id)
