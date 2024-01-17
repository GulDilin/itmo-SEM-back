import asyncio
import os
import sys
from typing import Generator, Type, Union

import pytest
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import schemas, services  # noqa
from app.core.keycloak import KeycloakClient, get_service_client  # noqa
from app.db.session import wrap_session  # noqa
from app.settings import settings  # noqa

load_dotenv()


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

    @staticmethod
    async def auth_test_client() -> str:
        KEYCLOAK_CLIENT_ID_TEST = os.getenv('KEYCLOAK_CLIENT_ID_TEST')
        KEYCLOAK_CLIENT_SECRET_TEST = os.getenv('KEYCLOAK_CLIENT_SECRET_TEST')
        kc = KeycloakClient(
            url=settings.KEYCLOAK_URL,
            realm=settings.KEYCLOAK_REALM,
            client_id=KEYCLOAK_CLIENT_ID_TEST,
            client_secret=KEYCLOAK_CLIENT_SECRET_TEST,
        )
        return await kc.get_active_access_token()

    @staticmethod
    def get_test_client_username() -> str:
        KEYCLOAK_CLIENT_ID_TEST = os.getenv('KEYCLOAK_CLIENT_ID_TEST')
        return f'service-account-{KEYCLOAK_CLIENT_ID_TEST}'


@pytest.fixture
def utils() -> Type[Utils]:
    return Utils
