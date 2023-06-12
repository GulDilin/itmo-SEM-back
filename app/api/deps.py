from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import entities
from app.db.session import get_session
from app.services import OrderService


async def get_tasks_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[OrderService, None]: yield OrderService(session)


async def get_path_task(
        task_service: OrderService = Depends(get_tasks_service),
        task_id: UUID = Path(None, title='Order ID'),
) -> entities.Order: return await task_service.read_one(id=str(task_id))
