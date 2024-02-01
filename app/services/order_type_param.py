from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class OrderTypeParamService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.OrderTypeParam,
            entity_name=message.MODEL_ORDER_TYPE_PARAM,
            sorting_fields=entities.OrderTypeParamSortingFields,
        )

    async def create(
        self,
        item: schemas.OrderTypeParamCreate,
        order_type: entities.OrderType,
    ) -> entities.OrderTypeParam:
        # TODO: add unique constraint for name + order_type_id
        return await self._create(
            item=entities.OrderTypeParam(
                name=item.name,
                value_type=item.value_type,
                required=item.required,
                order_type_id=order_type.id,
            )
        )
