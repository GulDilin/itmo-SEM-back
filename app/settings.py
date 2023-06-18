import os.path
from pathlib import Path
from typing import Dict

import toml
from pydantic import BaseSettings, validator

PROJECT_DIR = os.path.realpath(Path(__file__).parent.parent)
PYPROJECT_CONTENT = toml.load(f'{PROJECT_DIR}/pyproject.toml')['tool']['poetry']


class Settings(BaseSettings):
    class Config:
        env_file = os.path.join(PROJECT_DIR, '.env')
        case_sensitive = True

    ENVIRONMENT: str = 'DEV'
    BACKEND_CORS_ORIGINS: str = '*'
    DATABASE_URI: str = ''

    @validator('DATABASE_URI')
    def validate_db(cls, v: str, values: dict) -> str:  # noqa
        from sqlalchemy import create_engine
        try:
            print(f'DATABASE_URI={v}')
            db_url_parts = v.split(':', 2)
            if len(db_url_parts) > 1:
                db_url_parts[0] = db_url_parts[0].split('+', 2)[0]
            db_url = ':'.join(db_url_parts)
            print(f'{db_url=}')
            engine = create_engine(db_url)
            with engine.connect():
                pass
        except Exception:
            raise ValueError('''
                Failed to connect to DATABASE. Check DATABASE_URI variable.
            ''')
        return v

    KEYCLOAK_URL: str
    KEYCLOAK_URL_EXTERNAL: str
    KEYCLOAK_REALM: str
    KEYCLOAK_CLIENT_ID_FRONT: str
    KEYCLOAK_CLIENT_ID_SERIVCE: str
    KEYCLOAK_CLIENT_SECRET_SERIVCE: str
    KEYCLOAK_OPENID_CONFIG: Dict = {}

    @validator('KEYCLOAK_OPENID_CONFIG')
    def validate_keycloak(cls, v: str, values: dict) -> str:  # noqa
        import requests
        try:
            print(f'KEYCLOAK_URL={values["KEYCLOAK_URL"]}')
            open_id_config = requests.get(
                f'{values["KEYCLOAK_URL"]}/realms/{values["KEYCLOAK_REALM"]}/.well-known/openid-configuration'
            ).json()
            print(f'{open_id_config=}')
            return open_id_config
        except Exception:
            raise ValueError('''
                Failed to connect to KEYCLOAK. Check KEYCLOAK_URL and KEYCLOAK_REALM variable.
            ''')

    PROJECT_NAME: str = PYPROJECT_CONTENT['name']
    VERSION: str = PYPROJECT_CONTENT['version']
    DESCRIPTION: str = PYPROJECT_CONTENT['description']
    FORCE_HTTPS: bool = False


settings = Settings()
