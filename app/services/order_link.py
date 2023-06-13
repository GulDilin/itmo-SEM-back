from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderLinkService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.OrderLink,
            entity_name=message.MODEL_ORDER_LINK,
            sorting_fields=entities.OrderLinkSortingFields,
        )

    async def create(
            self,
            item: schemas.OrderLinkCreate,
    ) -> entities.Order:
        return await self._create(item=entities.OrderLink(
            order_left_id=item.order_left_id,
            order_right_id=item.order_right_id,
            link_type_id=item.link_type_id,
        ))
