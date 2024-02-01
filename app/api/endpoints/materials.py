from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post(
    "/{order_type_id}/order/{order_id}/materials/",
    response_model=schemas.Material,
)
async def create_material(
    item: schemas.MaterialCreate,
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    order: entities.Order = Depends(deps.get_path_order),
    materials_service: services.MaterialsService = Depends(
        deps.get_materials_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.Material:
    schemas.raise_order_type(user=user_data, order_type=str(order_type.name))
    return schemas.Material(
        **jsonable_encoder(
            await materials_service.create(
                item=item, user=user_data, order=order
            )
        )
    )


@router.get(
    "/{order_type_id}/order/{order_id}/materials/",
    response_model=schemas.PaginatedResponse,
)
async def get_materials(
    paginator: schemas.PaginationData = Depends(),
    order: entities.Order = Depends(deps.get_path_order),
    materials_service: services.MaterialsService = Depends(
        deps.get_materials_service
    ),
    sorting_list: schemas.SortingList = Depends(deps.get_sorting_list),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await materials_service.read_many_paginated(
            wrapper_class=schemas.Material,
            order_id=order.id,
            sorting_list=sorting_list,
            offset=paginator.offset,
            limit=paginator.limit,
        ),
        paginator,
    )


@router.get(
    "/{order_type_id}/order/{order_id}/materials/{material_id}/",
    response_model=schemas.Material,
)
async def get_material(
    material: entities.Material = Depends(deps.get_path_material),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.Material:
    return schemas.Material(**jsonable_encoder(material))


@router.put(
    "/{order_type_id}/order/{order_id}/materials/{material_id}/",
    response_model=schemas.Material,
)
async def update_material(
    update_data: schemas.MaterialUpdate,
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    material: entities.Material = Depends(deps.get_path_material),
    materials_service: services.MaterialsService = Depends(
        deps.get_materials_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> schemas.Material:
    schemas.raise_order_type(user=user_data, order_type=str(order_type.name))
    updated = await materials_service.update_by_user(
        id=str(material.id), user=user_data, **jsonable_encoder(update_data, exclude_none=True)
    )
    return schemas.Material(**jsonable_encoder(updated))


@router.delete("/{order_type_id}/order/{order_id}/materials/{material_id}/")
async def delete_material(
    order_type: entities.OrderType = Depends(deps.get_path_order_type),
    material: entities.Material = Depends(deps.get_path_material),
    materials_service: services.MaterialsService = Depends(
        deps.get_materials_service
    ),
    user_data: schemas.User = Depends(deps.get_user_data),
) -> None:
    schemas.raise_order_type(user=user_data, order_type=str(order_type.name))
    await materials_service.delete(id=material.id)
