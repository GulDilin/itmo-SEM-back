from typing import List

from fastapi import APIRouter
from fastapi_keycloak import FastAPIKeycloak, KeycloakUser

from app.settings import settings

idp = FastAPIKeycloak(
    server_url=f"{settings.KEYCLOAK_URL}/auth",
    client_id="test-client",
    client_secret="",
    admin_client_secret="XRCI7EKWIdnfr6m1IFUL6ejGCTNTVo1i",
    realm="Test",
    callback_uri="http://backend:5000/admin/callback"
)

router = APIRouter()


# Admin

@router.get("/users", tags=["user-management"])
def get_users() -> List[KeycloakUser]:
    return idp.get_all_users()
