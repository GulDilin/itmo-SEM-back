import pytest

from app.schemas.keycloak_user import UserRole


@pytest.mark.asyncio
async def test_get_random_user_id_by_role(utils) -> None:
    user_id = await utils.get_random_user_id_by_role(UserRole.STAFF)
    assert user_id


@pytest.mark.asyncio
async def test_auth_test_client(utils) -> None:
    token = await utils.auth_test_client()
    assert token
