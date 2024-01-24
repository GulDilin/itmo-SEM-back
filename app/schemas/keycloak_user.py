from typing import List, Union

from pydantic import BaseModel

from app.core.error import ActionForbidden

from .util import StrEnum


class KeycloakEndpoint(StrEnum):
    GET_CLIENTS = "{url}/admin/realms/{realm}/clients"
    GET_CLIENT = "{url}/admin/realms/{realm}/clients/{client_id}"
    GET_ROLE = "{url}/admin/realms/{realm}/clients/{client_id}/roles/{role_name}"
    GET_ROLES = "{url}/admin/realms/{realm}/clients/{client_id}/roles"
    GET_ROLE_USERS = (
        "{url}/admin/realms/{realm}/clients/{client_id}/roles/{role_name}/users"
    )
    GET_USERS = "{url}/admin/realms/{realm}/users"
    GET_USER = "{url}/admin/realms/{realm}/users/{user_id}"
    USER_ROLES = (
        "{url}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_id}"
    )
    CREATE_USER = "{url}/admin/realms/{realm}/users"
    GET_USER_ROLES = (
        "{url}/admin/realms/{realm}/users/{user_id}/role-mappings/clients/{client_id}"
    )
    GET_INSTALLATION_CONFIG = (
        "{url}/admin/realms/{realm}/clients/{client_id}"
        "/installation/providers/keycloak-oidc-keycloak-json"
    )


class UserRole(StrEnum):
    USER = "user"
    CUSTOMER = "customer"
    STAFF = "staff"
    STAFF_ORDER_MANAGER = "staff_order_manager"
    STAFF_CUSTOMER_MANAGER = "staff_customer_manager"
    STAFF_AXEMAN = "staff_axeman"
    STAFF_DELIVERY = "staff_delivery"
    STAFF_MAGICIAN = "staff_magician"
    STAFF_CRAFTSMAN = "staff_craftsman"
    ADMIN = "admin"


class User(BaseModel):
    user_id: str
    name: str
    roles: List[str]

    def check_one_role(self, roles: Union[str, List[str]]) -> None:
        roles = roles if isinstance(roles, list) else [roles]
        if len(set(roles).intersection(set(self.roles))) < 1:
            raise ActionForbidden

    def check_all_roles(self, roles: Union[str, List[str]]) -> None:
        roles = roles if isinstance(roles, list) else [roles]
        if not set(roles).issubset(set(self.roles)):
            raise ActionForbidden
