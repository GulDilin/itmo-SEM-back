import pytest

from app.core.keycloak import get_service_client
from app.schemas.keycloak_user import UserRole
from app.settings import settings


@pytest.mark.asyncio
async def test_get_random_user_id_by_role(utils) -> None:
    user_id = await utils.get_random_user_id_by_role(UserRole.STAFF)
    assert user_id


@pytest.mark.asyncio
async def test_auth_test_client(utils) -> None:
    token = await utils.auth_test_client()
    assert token


@pytest.mark.asyncio
async def test_assign_roles(utils) -> None:
    username = utils.get_test_client_username()
    print(f'{username=}')
    kc = get_service_client()
    user = await kc.get_user_by_username(username)
    user_id = user['id']
    client = await kc.get_client(settings.KEYCLOAK_CLIENT_ID_FRONT)
    client_id = client['id']
    roles_to_assign = [await kc.get_role_by_name(role_name=UserRole.STAFF)]
    await kc.add_user_roles(user_id, roles_to_assign)
    roles = await kc.get_user_roles(user_id, client_id)
    roles_names = [role['name'] for role in roles]
    print(f'{roles=}')
    await kc.clear_user_roles(user_id)
    assert UserRole.STAFF in roles_names
    roles = await kc.get_user_roles(user_id, client_id)
    print(f'{roles=}')
    assert not roles
