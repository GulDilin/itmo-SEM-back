from typing import AsyncGenerator, Any, Dict
from uuid import UUID

from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app import services, schemas
from app.core import auth
from app.db import entities
from app.db.session import get_session


async def get_order_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderService, None]: yield services.OrderService(session)


async def get_path_order(
        order_service: services.OrderService = Depends(get_order_service),
        order_id: UUID = Path(None, title='Order ID'),
) -> entities.Order: return await order_service.read_one(id=str(order_id))


async def get_order_type_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderTypeService, None]: yield services.OrderTypeService(session)


async def get_path_order_type(
        order_type_service: services.OrderTypeService = Depends(get_order_type_service),
        order_type_id: str = Path(None, title='Order Type ID'),
) -> entities.OrderType:
    try:
        UUID(str(order_type_id))
        return await order_type_service.read_one(id=str(order_type_id))
    except ValueError:
        return await order_type_service.read_one(name=str(order_type_id))


async def get_order_type_param_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderTypeParamService, None]: yield services.OrderTypeParamService(session)


async def get_path_order_type_param(
        order_type_param_service: services.OrderTypeParamService = Depends(get_order_type_param_service),
        order_type: entities.OrderType = Depends(get_path_order_type),
        order_type_param_id: str = Path(None, title='Order Type Param ID'),
) -> entities.OrderTypeParam:
    try:
        UUID(str(order_type_param_id))
        return await order_type_param_service.read_one(
            order_type_id=order_type.id, id=str(order_type_param_id)
        )
    except ValueError:
        return await order_type_param_service.read_one(
            order_type_id=order_type.id, name=str(order_type_param_id)
        )


async def get_path_order_type_param_by_order(
        order_type_param_service: services.OrderTypeParamService = Depends(get_order_type_param_service),
        order: entities.Order = Depends(get_path_order),
        order_type_param_id: str = Path(None, title='Order Type Param ID'),
) -> entities.OrderTypeParam:
    try:
        UUID(str(order_type_param_id))
        return await order_type_param_service.read_one(
            order_type_id=order.order_type_id, id=str(order_type_param_id)
        )
    except ValueError:
        return await order_type_param_service.read_one(
            order_type_id=order.order_type_id, name=str(order_type_param_id)
        )


async def get_order_param_value_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderParamValueService, None]: yield services.OrderParamValueService(session)


async def get_path_order_param_value(
        order: entities.Order = Depends(get_path_order),
        order_type_param: entities.OrderTypeParam = Depends(get_path_order_type_param_by_order),
        order_param_value_service: services.OrderParamValueService = Depends(get_order_param_value_service),
) -> entities.OrderParamValue:
    return await order_param_value_service.read_one(
        order_id=str(order.id),
        order_type_param_id=str(order_type_param.id),
    )


async def get_token(token: str = Depends(auth.oauth2_schema)) -> str:
    return token


async def get_token_data(
        token: str = Depends(get_token)
) -> AsyncGenerator[Dict[str, Any], None]:
    await auth.verify_token(token)
    yield auth.decode_auth_token(token)


async def get_user_data(
        token_data: dict = Depends(get_token_data),
) -> AsyncGenerator[schemas.User, None]:
    print(f'{token_data=}', flush=True)
    yield schemas.User(name=token_data['name'], roles=token_data['resource_access']['test-client']['roles'])
