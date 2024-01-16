from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderStatusUpdateService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.OrderStatusUpdate,
            entity_name=message.MODEL_ORDER,
            sorting_fields=entities.OrderStatusUpdateSortingFields,
        )

    async def create(
        self,
        user: schemas.User,
        order_id: str,
        new_order_status: schemas.OrderStatus,
        old_order_status: schemas.OrderStatus,
    ) -> entities.Order:
        return await self._create(
            item=entities.OrderStatusUpdate(
                order_id=order_id,
                new_status=new_order_status,
                old_status=old_order_status,
                user=user.user_id,
            )
        )
