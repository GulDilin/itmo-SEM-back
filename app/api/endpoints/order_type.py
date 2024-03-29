from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post("/", response_model=schemas.OrderType)
async def create_order_type(
    item: schemas.OrderTypeCreate,
    order_type_service: services.OrderTypeService = Depends(
        deps.get_order_type_service
    ),
    user_data: schemas.User = Depends(deps.CurrentUser()),
) -> schemas.OrderType:
    user_data.check_one_role([schemas.UserRole.STAFF])
    return schemas.OrderType(**jsonable_encoder(await order_type_service.create(item)))


@router.get("/", response_model=schemas.PaginatedResponse)
async def get_orders(
    paginator: schemas.PaginationData = Depends(),
    order_type_service: services.OrderTypeService = Depends(
        deps.get_order_type_service
    ),
    sorting_list: schemas.SortingList = Depends(deps.get_sorting_list),
    user_data: schemas.User = Depends(deps.CurrentUser()),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await order_type_service.read_many_paginated(
            wrapper_class=schemas.OrderType,
            offset=paginator.offset,
            sorting_list=sorting_list,
            limit=paginator.limit,
        ),
        paginator,
    )


@router.get("/{order_type_id}/", response_model=schemas.OrderType)
async def get_order(
    order: entities.OrderType = Depends(deps.get_path_order_type),
    user_data: schemas.User = Depends(deps.CurrentUser()),
) -> schemas.OrderType:
    return schemas.OrderType(**jsonable_encoder(order))


@router.put("/{order_type_id}/", response_model=schemas.OrderType)
async def update_order(
    update_data: schemas.OrderTypeUpdate,
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order_type_service: services.OrderTypeService = Depends(
        deps.get_order_type_service
    ),
    user_data: schemas.User = Depends(deps.CurrentUser()),
) -> schemas.OrderType:
    user_data.check_one_role([schemas.UserRole.STAFF])
    updated = await order_type_service.update(
        id=str(order_type.id), **jsonable_encoder(update_data, exclude_none=True)
    )
    return schemas.OrderType(**jsonable_encoder(updated))


@router.delete("/{order_type_id}/")
async def delete_order(
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order_type_service: services.OrderTypeService = Depends(
        deps.get_order_type_service
    ),
    user_data: schemas.User = Depends(deps.CurrentUser()),
) -> None:
    user_data.check_one_role([schemas.UserRole.STAFF])
    await order_type_service.delete(id=order_type.id)
