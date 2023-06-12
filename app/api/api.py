from fastapi import APIRouter

from app.api.endpoints import order

router = APIRouter()

router.include_router(order.router, prefix='/order', tags=['Order'])
