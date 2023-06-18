import base64
import json

from fastapi.security import OAuth2PasswordBearer

from app import schemas
from app.core import keycloak

oauth2_schema = OAuth2PasswordBearer(schemas.KeycloakEndpoint.TOKEN)


async def verify_token(token: str) -> None:
    try:
        await keycloak.get_service_client().verify_token(token)
    except Exception:
        raise ValueError('Token verification failed')


def decode_auth_token(token: str) -> dict:
    token_data = token.split(".")[1]
    return json.loads(base64.b64decode(bytes(token_data + '==', 'ascii')))
