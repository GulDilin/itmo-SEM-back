from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas, services
from app.api import deps, util
from app.db import entities

router = APIRouter()


@router.post('/', response_model=schemas.OrderLink)
async def create_order_link(
        order_link: schemas.OrderLinkCreate,
        order_link_service: services.OrderLinkService = Depends(deps.get_order_link_service),
) -> schemas.OrderLink:
    return schemas.OrderLink(**jsonable_encoder(
        await order_link_service.create(order_link)
    ))


@router.get('/', response_model=schemas.PaginatedResponse)
async def get_order_links(
        paginator: schemas.PaginationData = Depends(),
        order_link_service: services.OrderLinkService = Depends(deps.get_order_link_service),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await order_link_service.read_many_paginated(
            wrapper_class=schemas.OrderLink,
            offset=paginator.offset,
            limit=paginator.limit,
        ),
        paginator
    )


@router.delete('/{order_link_id}')
async def delete_order_link(
        order_link: entities.OrderLink = Depends(deps.get_path_order_link),
        order_link_service: services.OrderLinkService = Depends(deps.get_order_link_service),
) -> None:
    await order_link_service.delete(id=order_link.id)
