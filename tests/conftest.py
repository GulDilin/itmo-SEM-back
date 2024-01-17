import asyncio
import os
import sys
from typing import Generator, Type, Union

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import schemas, services  # noqa
from app.core.keycloak import get_service_client  # noqa
from app.db.session import wrap_session  # noqa


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class Utils:
    @staticmethod
    async def get_random_user_id_by_role(role_name: str) -> Union[str, None]:
        kc = get_service_client()
        if data := await kc.get_role_with_users(role_name=role_name):
            return data[0]['id']
        return None

    @staticmethod
    async def get_random_user_id_customer() -> Union[str, None]:
        return await Utils.get_random_user_id_by_role(schemas.UserRole.CUSTOMER)

    @staticmethod
    async def get_random_user_id_order_manager() -> Union[str, None]:
        return await Utils.get_random_user_id_by_role(schemas.UserRole.STAFF_ORDER_MANAGER)

    @staticmethod
    async def get_order_type_id() -> Union[str, None]:
        async with wrap_session() as session:
            order_type_service = services.OrderTypeService(session)
            items = await order_type_service.read_many()
            return items[0].id


@pytest.fixture
def utils() -> Type[Utils]:
    return Utils
