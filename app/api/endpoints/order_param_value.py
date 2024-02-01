from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post(
    "/{order_type_id}/order/{order_id}/params/{order_type_param_id}/",
    response_model=schemas.OrderParamValue,
)
async def create_order_type(
    item: schemas.OrderParamValueCreate,
    order: entities.Order = Depends(deps.get_path_order),
    order_type_param: entities.OrderTypeParam = Depends(
        deps.get_path_order_type_param_by_order
    ),
    order_param_value_service: services.OrderParamValueService = Depends(
        deps.get_order_param_value_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.OrderParamValue:
    user_data.check_one_role([schemas.UserRole.STAFF])
    return schemas.OrderParamValue(
        **jsonable_encoder(
            await order_param_value_service.create(
                item=item, order=order, order_type_param=order_type_param
            )
        )
    )


@router.get(
    "/{order_type_id}/order/{order_id}/params/",
    response_model=schemas.PaginatedResponse,
)
async def get_orders(
    paginator: schemas.PaginationData = Depends(),
    order: entities.Order = Depends(deps.get_path_order),
    order_param_value_service: services.OrderParamValueService = Depends(
        deps.get_order_param_value_service
    ),
    sorting_list: schemas.SortingList = Depends(deps.get_sorting_list),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await order_param_value_service.read_many_paginated(
            wrapper_class=schemas.OrderParamValue,
            order_id=order.id,
            sorting_list=sorting_list,
            offset=paginator.offset,
            limit=paginator.limit,
        ),
        paginator,
    )


@router.get(
    "/{order_type_id}/order/{order_id}/params/{order_type_param_id}/",
    response_model=schemas.OrderParamValue,
)
async def get_order_param(
    order_param_value: entities.OrderTypeParam = Depends(
        deps.get_path_order_param_value
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.OrderParamValue:
    return schemas.OrderParamValue(**jsonable_encoder(order_param_value))


@router.put(
    "/{order_type_id}/order/{order_id}/params/{order_type_param_id}/",
    response_model=schemas.OrderParamValue,
)
async def update_order_param(
    update_data: schemas.OrderParamValueUpdate,
    order_param_value: entities.OrderTypeParam = Depends(
        deps.get_path_order_param_value
    ),
    order_param_value_service: services.OrderParamValueService = Depends(
        deps.get_order_param_value_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.OrderParamValue:
    user_data.check_one_role([schemas.UserRole.STAFF])
    updated = await order_param_value_service.update(
        id=str(order_param_value.id), **jsonable_encoder(update_data, exclude_none=True)
    )
    return schemas.OrderParamValue(**jsonable_encoder(updated))


@router.delete("/{order_type_id}/order/{order_id}/params/{order_type_param_id}/")
async def delete_order_param(
    order_param_value: entities.OrderTypeParam = Depends(
        deps.get_path_order_param_value
    ),
    order_param_value_service: services.OrderParamValueService = Depends(
        deps.get_order_param_value_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> None:
    user_data.check_one_role([schemas.UserRole.STAFF])
    await order_param_value_service.delete(id=order_param_value.id)
