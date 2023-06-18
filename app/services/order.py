from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.Order,
            entity_name=message.MODEL_ORDER,
            sorting_fields=entities.OrderSortingFields,
        )

    async def create(
            self,
            item: schemas.OrderCreate,
            order_type: entities.OrderType,
    ) -> entities.Order:
        return await self._create(item=entities.Order(
            status=schemas.OrderStatus.NEW,
            user_customer=item.user_customer,
            user_implementer=item.user_implementer,
            parent_order_id=item.parent_order_id,
            order_type_id=order_type.id,
        ))
