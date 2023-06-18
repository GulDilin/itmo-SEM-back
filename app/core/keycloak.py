from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from app import schemas
from app.core import error, message
from app.settings import settings

# REST API DOCS: https://www.keycloak.org/docs-api/20.0.5/rest-api/index.html


class KeycloakAuthEndpointKey(schemas.StrEnum):
    AUTH = 'authorization_endpoint'
    TOKEN = 'token_endpoint'
    INTROSPECT = 'introspection_endpoint'
    USER_INFO = 'userinfo_endpoint'


@dataclass
class KeycloakClient:
    url: str
    realm: str
    client_id: str
    client_secret: Optional[str] = None

    @staticmethod
    def get_token_auth_headers(token: str) -> Dict:
        return {
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    def get_url_for(key: KeycloakAuthEndpointKey) -> str:
        return settings.KEYCLOAK_OPENID_CONFIG[key]

    async def get_token_by_secret(self) -> str:
        if not self.client_secret:
            raise ValueError('Client secret not specified')

        async with httpx.AsyncClient() as client:
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'client_credentials',
                'client_secret': self.client_secret,
                'client_id': self.client_id,
            }
            url = self.get_url_for(KeycloakAuthEndpointKey.TOKEN).format(
                url=self.url,
                realm=self.realm,
            )
            response = await client.post(url, data=data, headers=headers)
            return response.json().get('access_token')

    async def get_client(self, client_id: str) -> Dict:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_CLIENTS.value.format(
            url=self.url,
            realm=self.realm,
        )
        params = {'clientId': client_id}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if len(data) < 1:
                raise error.ItemNotFound(item=message.MODEL_AUTH_CLIENT)
            return response.json()[0]

    async def get_clients(self) -> List:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_CLIENTS.value.format(
            url=self.url,
            realm=self.realm,
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def verify_token(self, token: str) -> None:
        url = self.get_url_for(KeycloakAuthEndpointKey.INTROSPECT).format(
            url=self.url,
            realm=self.realm,
        )
        data = {
            'grant_type': 'client_credentials',
            'client_secret': self.client_secret,
            'client_id': self.client_id,
            'token': token,
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, data=data)
                response.raise_for_status()
        except Exception:
            raise error.Unauthorized

    async def get_users(self) -> List:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_USERS.value.format(
            url=self.url,
            realm=self.realm,
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                data = []
            return data

    async def get_user_by_id(self, user_id: str) -> Dict:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_USER.value.format(
            url=self.url,
            realm=self.realm,
            user_id=user_id,
        )
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception:
            raise error.ItemNotFound(item=message.MODEL_USER)

    async def get_user_roles(self, user_id: str, client_id: str) -> Dict:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_USER_ROLES.value.format(
            url=self.url,
            realm=self.realm,
            user_id=user_id,
            client_id=client_id,
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()


def get_service_client() -> KeycloakClient:
    return KeycloakClient(
        url=settings.KEYCLOAK_URL,
        realm=settings.KEYCLOAK_REALM,
        client_id=settings.KEYCLOAK_CLIENT_ID_SERIVCE,
        client_secret=settings.KEYCLOAK_CLIENT_SECRET_SERIVCE
    )