from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import entities
from app.db.session import get_session
from app.services import TaskService


async def get_tasks_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[TaskService, None]: yield TaskService(session)


async def get_path_task(
        task_service: TaskService = Depends(get_tasks_service),
        task_id: UUID = Path(None, title='Task ID'),
) -> entities.Task: return await task_service.read_one(id=str(task_id))
