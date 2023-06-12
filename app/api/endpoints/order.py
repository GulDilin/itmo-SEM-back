from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder

from app import schemas
from app.api import deps, util
from app.db import entities
from app.services import OrderService

router = APIRouter()


@router.post('/', response_model=schemas.Order)
async def create_task(
        task: schemas.OrderCreate,
        task_service: OrderService = Depends(deps.get_tasks_service),
) -> schemas.Order:
    return schemas.Order(**jsonable_encoder(await task_service.create(task)))


@router.get('/', response_model=schemas.PaginatedResponse)
async def get_tasks(
    paginator: schemas.PaginationData = Depends(),
    task_service: OrderService = Depends(deps.get_tasks_service),
) -> schemas.PaginatedResponse:
    return await util.get_paginated_response(
        await task_service.read_many_paginated(
            wrapper_class=schemas.Order,
            offset=paginator.offset,
            limit=paginator.limit,
        ),
        paginator
    )


@router.get('/{task_id}', response_model=schemas.Order)
async def get_task(
    task: entities.Order = Depends(deps.get_path_task),
) -> schemas.Order:
    return schemas.Order(**jsonable_encoder(task))


@router.put('/{task_id}', response_model=schemas.Order)
async def update_task(
    task_update_data: schemas.OrderUpdate,
    task: entities.Order = Depends(deps.get_path_task),
    task_service: OrderService = Depends(deps.get_tasks_service),
) -> schemas.Order:
    updated = await task_service.update(id=str(task.id), **jsonable_encoder(task_update_data))
    return schemas.Order(**jsonable_encoder(updated))


@router.delete('/{task_id}')
async def delete_task(
    task: entities.Order = Depends(deps.get_path_task),
    task_service: OrderService = Depends(deps.get_tasks_service),
) -> None:
    await task_service.delete(id=task.id)
