# https://fastapi.tiangolo.com/tutorial/testing/

from app.db.session import wrap_session, async_engine
from app.db import entities
from app import schemas
from app.services import OrderTypeService
import pytest

@pytest.mark.asyncio
async def test_tables_exist() -> None:
    conn = async_engine.connect()
    entities.OrderType.__tablename__
    attrs = ['name', 'dep_type']
    res = async_engine.dialect.has_table(conn, entities.OrderType.__tablename__)
    print(f'{res=}')
    assert res == True
    # entities.OrderType.__tablename__


@pytest.mark.asyncio
async def test_create() -> None:
    async with wrap_session() as session:
        order_type_service = OrderTypeService(session)
        create_model = schemas.OrderTypeCreate(name="test")
        created = await order_type_service.create(create_model)
        got = await order_type_service.read_one(id=str(created.id))
        assert got == created
        assert got.name == create_model.name

@pytest.mark.asyncio
async def test_get() -> None:
    async with wrap_session() as session:
        order_type_service = OrderTypeService(session)
        items = await order_type_service.read_many()
        assert len(items) > 0
