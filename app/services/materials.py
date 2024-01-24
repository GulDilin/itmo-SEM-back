from typing import Any, Union
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas
from app.core import message
from app.db import entities

from .base import BaseService


class MaterialsService(BaseService):
    def __init__(self, db_session: AsyncSession):
        super().__init__(
            db_session=db_session,
            entity=entities.Material,
            entity_name=message.MODEL_MATERIAL,
            sorting_fields=entities.MaterialSortingFields,
        )

    async def create(
        self,
        item: schemas.MaterialCreate,
        user: schemas.User,
        order: entities.Order,
    ) -> entities.Material:
        return await self._create(
            item=entities.Material(
                name=item.name,
                amount=item.amount,
                value_type=item.value_type,
                item_price=item.item_price,
                user_creator=user.user_id,
                user_updator=user.user_id,
                order_id=order.id,
            )
        )

    async def update_by_user(self, id: Union[UUID, str], user: schemas.User, **kwargs: Any) -> Any:
        if 'user_creator' in kwargs:
            kwargs.pop('user_creator')
        kwargs['user_updator'] = user.user_id
        return await super().update(id=id, **kwargs)
