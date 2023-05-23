from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class TaskService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.Task,
            entity_name=message.MODEL_TASK,
            sorting_fields=entities.TaskSortingFields,
        )

    async def create(self, item: schemas.TaskCreate) -> entities.Task:
        return await self._create(item=entities.Task(
            content=item.content
        ))
