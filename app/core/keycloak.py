import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from app import schemas
from app.core import auth, error, message
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
    exp_threshold: int = 50
    _access_token: Optional[str] = None

    @staticmethod
    def get_token_auth_headers(token: str) -> Dict:
        return {
            "Authorization": f"Bearer {token}",
        }

    @staticmethod
    def get_url_for(key: KeycloakAuthEndpointKey) -> str:
        return settings.KEYCLOAK_OPENID_CONFIG[key]

    async def get_auth_config(self, client_id: str, token: Optional[str] = None) -> Dict:
        token = token if token else await self.get_active_access_token()
        client_k = await self.get_client(client_id, token=token)
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_INSTALLATION_CONFIG.value.format(
            url=self.url,
            realm=self.realm,
            client_id=client_k['id'],
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def set_access_token_and_return(self) -> str:
        self._access_token = await self.get_token_by_secret()
        return self._access_token

    async def get_active_access_token(self) -> str:
        if not self._access_token:
            return await self.set_access_token_and_return()
        token_data = auth.decode_auth_token(self._access_token)
        if (int(token_data.get('exp', 0)) - time.time()) < self.exp_threshold:
            return await self.set_access_token_and_return()
        return self._access_token

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
            url = self.get_url_for(KeycloakAuthEndpointKey.TOKEN)
            response = await client.post(url, data=data, headers=headers)
            response.raise_for_status()
            return response.json().get('access_token')

    async def get_client(self, client_id: str, token: Optional[str] = None) -> Dict:
        token = token if token else await self.get_active_access_token()
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

    async def get_clients(self, token: Optional[str] = None) -> List:
        token = token if token else await self.get_active_access_token()
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
        url = self.get_url_for(KeycloakAuthEndpointKey.INTROSPECT)
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

    async def get_roles(self, token: Optional[str] = None) -> List:
        token = token if token else await self.get_active_access_token()
        headers = self.get_token_auth_headers(token)
        client_id = (
            await self.get_client(
                client_id=settings.KEYCLOAK_CLIENT_ID_FRONT,
                token=token))['id']
        url = schemas.KeycloakEndpoint.GET_ROLES.value.format(
            url=self.url,
            realm=self.realm,
            client_id=client_id
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                data = []
            return data

    async def get_role_with_users(self, role_name: str, token: Optional[str] = None) -> List:
        token = token if token else await self.get_active_access_token()
        headers = self.get_token_auth_headers(token)
        client_id = (
            await self.get_client(
                client_id=settings.KEYCLOAK_CLIENT_ID_FRONT,
                token=token))['id']
        url = schemas.KeycloakEndpoint.GET_ROLE_USERS.value.format(
            url=self.url,
            realm=self.realm,
            client_id=client_id,
            role_name=role_name
        )
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if len(data) == 0:
                data = []
            return data

    async def get_users(self, token: Optional[str] = None) -> List:
        token = token if token else await self.get_active_access_token()
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

    async def get_users_with_roles(self, token: Optional[str] = None) -> List:
        token = token if token else await self.get_active_access_token()
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
            client_id = (
                await self.get_client(
                    client_id=settings.KEYCLOAK_CLIENT_ID_FRONT,
                    token=token))['id']
            for d in data:
                d['roles'] = await self.get_user_roles(
                    client_id=client_id,
                    token=token,
                    user_id=d['id'])
            return data

    async def get_user_by_id(self, user_id: str, token: Optional[str] = None) -> Dict:
        token = token if token else await self.get_active_access_token()
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

    async def get_user_roles(self, user_id: str, client_id: str, token: Optional[str] = None) -> Dict:
        token = token if token else await self.get_active_access_token()
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
