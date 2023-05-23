from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.settings import settings

sqlalchemy_database_uri = settings.DATABASE_URI

async_engine = create_async_engine(sqlalchemy_database_uri, pool_pre_ping=True)
async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            yield session


@asynccontextmanager
async def wrap_session() -> AsyncGenerator:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
