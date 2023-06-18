from dataclasses import dataclass
from typing import Dict, List, Optional

import httpx

from app import schemas
from app.core import error
from app.log import logger
from app.settings import settings

# REST API DOCS: https://www.keycloak.org/docs-api/20.0.5/rest-api/index.html


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
            url = schemas.KeycloakEndpoint.TOKEN.value.format(
                url=self.url,
                realm=self.realm,
            )
            response = await client.post(url, data=data, headers=headers)
            logger.info(f'{response.json()=}')
            return response.json().get('access_token')

    async def get_client(self, client_id: str) -> Dict:
        token = await self.get_token_by_secret()
        headers = self.get_token_auth_headers(token)
        url = schemas.KeycloakEndpoint.GET_CLIENTS.value.format(
            url=self.url,
            realm=self.realm,
            # client_id=client_id,
        )
        params = {'clientId': client_id}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            if len(data) < 1:
                raise error.ItemNotFound(item='Auth Client')
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
        url = schemas.KeycloakEndpoint.INTROSPECT.value.format(
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
                logger.info(f'introspect={response.json()}')
                response.raise_for_status()
        except Exception:
            raise ValueError('Token verification failed')

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
            logger.info(f'{response.json()=}')
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
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

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
