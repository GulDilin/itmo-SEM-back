from fastapi import APIRouter

from app.api.endpoints import tasks

router = APIRouter()

router.include_router(tasks.router, prefix='/tasks', tags=['Tasks'])
