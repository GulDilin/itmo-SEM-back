from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderTypeService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.OrderType,
            entity_name=message.MODEL_ORDER_TYPE,
            sorting_fields=entities.OrderTypeSortingFields,
        )

    async def create(self, item: schemas.OrderTypeCreate) -> entities.Order:
        return await self._create(
            item=entities.OrderType(
                name=item.name,
            )
        )
