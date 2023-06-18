from typing import List

from pydantic import BaseModel

from app.core.error import ActionForbidden


class KeycloakEndpoint:
    USER_INFO = '{url}/auth/admin/realms/{realm}/protocol/openid-connect/userinfo'


class User(BaseModel):
    name: str
    roles: List[str]

    def raise_has_role(self) -> None:
        raise ActionForbidden('User does not have proper role')
