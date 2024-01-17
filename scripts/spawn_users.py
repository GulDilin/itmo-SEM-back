import asyncio
import json
import os
import sys
import traceback
from typing import Dict, List

import httpx
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Fix import for app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv("../.env")

DATABASE_URI = os.getenv("DATABASE_URI")

print(f'{DATABASE_URI=}')
sqlalchemy_database_uri = DATABASE_URI

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)


async def create_users(users_list: List[Dict[str, str]]) -> None:
    from app.core import error
    from app.core.keycloak import get_service_client
    from app.settings import settings

    kc = get_service_client()
    for user_dict in users_list:
        try:
            user = await kc.get_user_by_username(user_dict['username'])
            if user:
                client = await kc.get_client(settings.KEYCLOAK_CLIENT_ID_FRONT)
                user_roles = await kc.get_user_roles(user_id=user['id'], client_id=client['id'])
                user_roles_names = [role.name for role in user_roles]
                print(f"User {user_dict['username']} {user_roles=} already created")
                roles_names = [role for role in user_dict['roles'] if role not in user_roles_names]
                if len(roles_names) < 1:
                    continue
                print(f"User {user_dict['username']} dont have roles {roles_names}")
                roles = [await kc.get_role_by_name(role_name=it) for it in roles_names]
                await kc.add_user_roles(
                    user_id=user['id'],
                    roles=roles,
                )
                print(f"Assign roles {roles_names} to user {user_dict['username']}")
                continue
        except error.ItemNotFound:
            pass

        try:
            user = {
                'username': user_dict['username'],
                'password': user_dict['password'],
            }
            print(f"Create user {user_dict['username']}")
            await kc.create_user(user)
            user = await kc.get_user_by_username(user_dict['username'])
            roles = [await kc.get_role_by_name(role_name=it) for it in user_dict['roles']]
            await kc.add_user_roles(
                user_id=user['id'],
                roles=roles,
            )
        except httpx.HTTPStatusError as ex:
            print(f"User creation error {traceback.format_exc()}")
            if ex.response:
                print(f"Response {ex.response.text}")
        except Exception:
            print(f"User creation error {traceback.format_exc()}")

if __name__ == '__main__':
    users_dict = {}
    with open('./users.json') as f:
        users_dict = json.load(f)
    users_list = users_dict.get("users", [])
    asyncio.run(create_users(users_list))
    print("Users successfully created.")
