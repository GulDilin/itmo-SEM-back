from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from ..schemas.order import OrderTypeName
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
        if order_type.name != OrderTypeName.BATH_ORDER and item.parent_order_id is None:
            raise ValueError("Заполните родительский заказ")

        if item.parent_order_id is not None:
            child_orders = await self.read_many(parent_order_id=item.parent_order_id)
            for order in child_orders:
                if order.order_type_id == order_type.id:
                    raise ValueError("Заявка с таким типом уже была создана")

        return await self._create(
            item=entities.Order(
                status=schemas.OrderStatus.NEW,
                user_customer=item.user_customer,
                user_implementer=item.user_implementer,
                parent_order_id=item.parent_order_id,
                order_type_id=order_type.id,
            )
        )
