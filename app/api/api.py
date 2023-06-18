from fastapi import APIRouter

from app.api.endpoints import (admin, order, order_param_value, order_type,
                               order_type_param)

router = APIRouter()

router.include_router(order_type.router, prefix='/order_type', tags=['Order Type'])
router.include_router(order_type_param.router, prefix='/order_type', tags=['Order Type Prams'])
router.include_router(order.router, prefix='/order_type', tags=['Order'])
router.include_router(order_param_value.router, prefix='/order_type', tags=['Order Params'])
router.include_router(admin.router, prefix='/admin', tags=['Admin'])
