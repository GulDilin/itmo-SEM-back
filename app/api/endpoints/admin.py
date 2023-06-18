from typing import Dict

from fastapi import APIRouter, Depends

from app import schemas
from app.api import deps
from app.core import keycloak
from app.settings import settings

router = APIRouter()


@router.get("/users", response_model=schemas.PaginatedResponse)
async def get_users(
    user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF])),
) -> schemas.PaginatedResponse:
    kc = keycloak.get_service_client()
    users = await kc.get_users()
    # TODO: add roles to users
    return schemas.PaginatedResponse(
        results=users,
        count=len(users),
        next=None,
        previous=None,
    )


@router.get("/auth/config")
async def get_auth_config() -> Dict:
    kc = keycloak.get_service_client()
    # client = await kc.get_client(client_id=settings.KEYCLOAK_CLIENT_ID_FRONT)
    return await kc.get_auth_config(client_id=settings.KEYCLOAK_CLIENT_ID_FRONT)


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    user_data: schemas.User = Depends(deps.CurrentUser())
) -> Dict:
    if user_data.user_id != user_id:
        user_data.check_one_role(schemas.UserRole.STAFF)
    kc = keycloak.get_service_client()
    user = await kc.get_user_by_id(user_id)
    client = await kc.get_client(client_id=settings.KEYCLOAK_CLIENT_ID_FRONT)
    roles = await kc.get_user_roles(user_id=user_id, client_id=client['id'])
    user['roles'] = roles
    return user


@router.get("/service-token-test")
async def test() -> Dict:
    # TODO: remove endpoint
    kc = keycloak.get_service_client()
    token = await kc.get_token_by_secret()
    return {'token': token}


@router.get("/verify_staff")
async def verify_staff(
    user: schemas.User = Depends(deps.CurrentUser([schemas.UserRole.STAFF]))
) -> schemas.User:
    # TODO: remove endpoint
    user.check_one_role([schemas.UserRole.STAFF, schemas.UserRole.USER])
    user.check_one_role(schemas.UserRole.STAFF)
    user.check_all_roles([schemas.UserRole.STAFF, schemas.UserRole.USER])
    return user
