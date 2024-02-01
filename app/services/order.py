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
        if str(order_type.dep_type) != schemas.OrderDepType.MAIN and item.parent_order_id is None:
            raise ValueError(message.ERROR_NO_PARENT_ORDER)

        if item.parent_order_id is not None:
            same_type_exists = await self.exists(parent_order_id=item.parent_order_id, order_type_id=order_type.id)
            if (same_type_exists):
                raise ValueError(message.ERROR_ORDER_WITH_TYPE_EXISTS)

        return await self._create(
            item=entities.Order(
                status=schemas.OrderStatus.NEW,
                user_customer=item.user_customer,
                user_implementer=item.user_implementer,
                parent_order_id=item.parent_order_id,
                order_type_id=order_type.id,
            )
        )
