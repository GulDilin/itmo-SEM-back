from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderParamValueService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.OrderParamValue,
            entity_name=message.MODEL_ORDER_PARAM_VALUE,
            sorting_fields=entities.OrderParamValueSortingFields,
        )

    async def create(
        self,
        item: schemas.OrderParamValueCreate,
        order: entities.Order,
        order_type_param: entities.OrderTypeParam,
    ) -> entities.OrderParamValue:
        return await self._create(item=entities.OrderParamValue(
            value=item.value,
            order_id=order.id,
            order_type_param_id=order_type_param.id,
        ))
