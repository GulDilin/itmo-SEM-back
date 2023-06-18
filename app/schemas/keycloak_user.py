from typing import List

from pydantic import BaseModel

from app.core.error import ActionForbidden

from .util import StrEnum


class KeycloakEndpoint(StrEnum):
    USER_INFO = '{url}/admin/realms/{realm}/protocol/openid-connect/userinfo'
    INTROSPECT = '{url}/realms/{realm}/protocol/openid-connect/token/introspect'
    TOKEN = '{url}/realms/{realm}/protocol/openid-connect/token'
    GET_CLIENTS = '{url}/admin/realms/{realm}/clients'
    GET_CLIENT = '{url}/admin/realms/{realm}/clients/{client_id}'
    GET_USERS = '{url}/admin/realms/{realm}/users'
    GET_USER = '{url}/admin/realms/{realm}/users/{user_id}'
    GET_USER_ROLES = '{url}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_id}'


class User(BaseModel):
    name: str
    roles: List[str]

    def raise_has_role(self) -> None:
        raise ActionForbidden('User does not have proper role')
