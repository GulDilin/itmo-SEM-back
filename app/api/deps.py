from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from uuid import UUID

from fastapi import Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, services
from app.api import util
from app.core import auth
from app.db import entities
from app.db.session import get_session
from app.log import logger


async def get_order_type_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderTypeService, None]: yield services.OrderTypeService(session)


async def get_path_order_type(
        order_type_service: services.OrderTypeService = Depends(get_order_type_service),
        order_type_id: str = Query(None, title='Order Type ID'),
) -> Optional[entities.OrderType]:
    if order_type_id is None:
        return None
    try:
        UUID(str(order_type_id))
        return await order_type_service.read_one(id=str(order_type_id))
    except ValueError:
        return await order_type_service.read_one(name=str(order_type_id))


async def get_order_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderService, None]: yield services.OrderService(session)


async def get_update_status_service(
        session: AsyncSession = Depends(get_session)
) -> AsyncGenerator[services.OrderStatusUpdateService, None]: yield services.OrderStatusUpdateService(session)


async def get_path_order(
        order_type: Optional[entities.OrderType] = Depends(get_path_order_type),
        order_service: services.OrderService = Depends(get_order_service),
        order_id: UUID = Path(None, title='Order ID'),
) -> entities.Order:
    filter_data = {}
    if order_type:
        filter_data['order_type_id'] = str(order_type.id)
    return await order_service.read_one(
        id=str(order_id),
        load_props=['order_type.params'],
        **filter_data,
    )


def get_order_filter(
    id: Optional[List[str]] = Query(None),
    parent_order_id: Optional[List[str]] = Query(None),
    user_customer: Optional[List[str]] = Query(None),
    user_implementer: Optional[List[str]] = Query(None),
    status: Optional[List[str]] = Query(None),
    dep_type: Optional[List[str]] = Query(None),
) -> dict:
    return schemas.OrderFilter(
        id=id,
        parent_order_id=parent_order_id,
        user_customer=user_customer,
        user_implementer=user_implementer,
        status=status,
        dep_type=dep_type,
    ).dict(exclude_none=True)


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


async def get_token(token: HTTPAuthorizationCredentials = Depends(auth.oauth2_schema)) -> str:
    logger.info(f'{token=}')
    return token.credentials


async def get_token_data(
        token: str = Depends(get_token)
) -> AsyncGenerator[Dict[str, Any], None]:
    await auth.verify_token(token)
    yield auth.decode_auth_token(token)


async def get_user_data(
        token_data: dict = Depends(get_token_data),
) -> AsyncGenerator[schemas.User, None]:
    logger.info(f'{token_data=}')
    yield schemas.User(
        user_id=token_data['sub'],
        name=token_data['preferred_username'],
        roles=token_data['roles'],
    )


class CurrentUser:
    def __init__(self, required_roles: Optional[Union[str, List[str]]] = None):
        self.required_roles = required_roles

    async def __call__(
            self,
            user: schemas.User = Depends(get_user_data),
    ) -> schemas.User:
        if self.required_roles:
            user.check_all_roles(self.required_roles)
        return user


def get_sorting_list(sort: Optional[str] = None) -> Optional[schemas.SortingList]:
    if sort is None:
        return schemas.SortingList(
            sorting_list=[
                schemas.SortingListItem(type=schemas.SortingType.DESC, field="created_at")
            ]
        )

    class SortValueChecker(BaseModel):
        sort: Optional[str] = Field(None, max_length=200)

    SortValueChecker(sort=sort)
    sorting_list = util.parse_sorting(sort)
    return sorting_list
