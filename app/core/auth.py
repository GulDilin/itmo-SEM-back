import base64
import json

from fastapi.security import HTTPBearer

from app.core import keycloak

oauth2_schema = HTTPBearer()


async def verify_token(token: str) -> None:
    await keycloak.get_service_client().verify_token(token)


def decode_auth_token(token: str) -> dict:
    token_data = token.split(".")[1]
    return json.loads(base64.b64decode(bytes(token_data + "==", "ascii")))
