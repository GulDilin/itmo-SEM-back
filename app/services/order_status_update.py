from typing import Dict, List

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
            sorting_fields=entities.OrderStatusUpdatenSortingFields,
        )
        self.allowed_status_transitions: Dict[str, List[str]] = {
            schemas.OrderStatus.NEW: [schemas.OrderStatus.READY],
            schemas.OrderStatus.READY: [schemas.OrderStatus.NEW, schemas.OrderStatus.IN_PROGRESS],
            schemas.OrderStatus.IN_PROGRESS: [schemas.OrderStatus.DONE],
            schemas.OrderStatus.DONE: [schemas.OrderStatus.ACCEPTED, schemas.OrderStatus.READY],
            schemas.OrderStatus.ACCEPTED: [],
        }

    async def create(
            self,
            user: schemas.User,
            order_id: str,
            new_order_status: schemas.OrderStatus,
            old_order_status: schemas.OrderStatus,
    ) -> entities.Order:
        if new_order_status not in self.allowed_status_transitions[old_order_status]:
            raise ValueError(f'Could not transition from {old_order_status} to {new_order_status}')
        return await self._create(item=entities.OrderStatusUpdate(
            order_id=order_id,
            new_status=new_order_status,
            old_status=old_order_status,
            user=user.user_id
        ))
