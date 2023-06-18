import base64
import json

import httpx
from fastapi.security import OAuth2PasswordBearer

from app import schemas
from app.settings import settings

openid_url = f'{settings.KEYCLOAK_URL}/auth/admin/realms/{settings.KEYCLOAK_REALM}/protocol/openid-connect'
verify_url = f'{openid_url}/userinfo'
token_url = f'{openid_url}/token'
auth_url = f'{openid_url}/auth'

oauth2_schema = OAuth2PasswordBearer(
    token_url,
)


async def verify_token(token: str) -> dict:
    userinfo_url = schemas.KeycloakEndpoint.USER_INFO.format(
        url=settings.KEYCLOAK_URL,
        realm=settings.KEYCLOAK_REALM
    )
    try:
        headers = {
            "Authorization": f"Bearer {token}",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_url, headers=headers)
            return response.json()
    except Exception:
        raise ValueError('Token verification failed')


def decode_auth_token(token: str) -> dict:
    token_data = token.split(".")[1]
    return json.loads(base64.b64decode(bytes(token_data + '==', 'ascii')))
