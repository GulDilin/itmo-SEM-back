import os.path
from pathlib import Path

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

    PROJECT_NAME: str = PYPROJECT_CONTENT['name']
    VERSION: str = PYPROJECT_CONTENT['version']
    DESCRIPTION: str = PYPROJECT_CONTENT['description']
    FORCE_HTTPS: bool = False


settings = Settings()
