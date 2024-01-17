# https://fastapi.tiangolo.com/tutorial/testing/

from typing import Tuple

import pytest
from sqlalchemy import inspect

from app import schemas, services
from app.db import entities
from app.db.session import async_engine, wrap_session

entities_l = [
    entities.OrderType,
    entities.OrderTypeParam,
    entities.Order,
    entities.OrderParamValue,
    entities.OrderConfirmation,
    entities.OrderStatusUpdate,
]
default_cols = {
    "id": "VARCHAR(36)",
    "created_at": "TIMESTAMP",
    "updated_at": "TIMESTAMP",
}
entities_columns = {
    str(entities.OrderType.__tablename__): {
        **default_cols,
        "name": "VARCHAR(100)",
        "dep_type": "VARCHAR(50)",
    },
    str(entities.OrderTypeParam.__tablename__): {
        **default_cols,
        "name": "VARCHAR(100)",
        "value_type": "VARCHAR(100)",
        "required": "BOOLEAN",
        "order_type_id": "VARCHAR(50)",
    },
    str(entities.Order.__tablename__): {
        **default_cols,
        "status": "VARCHAR(100)",
        "user_customer": "VARCHAR(100)",
        "user_implementer": "VARCHAR(100)",
        "order_type_id": "VARCHAR(50)",
        "parent_order_id": "VARCHAR(50)",
    },
    str(entities.OrderParamValue.__tablename__): {
        **default_cols,
        "value": "VARCHAR(100)",
        "order_type_param_id": "VARCHAR(50)",
        "order_id": "VARCHAR(50)",
    },
    str(entities.OrderConfirmation.__tablename__): {
        **default_cols,
        "user": "VARCHAR(100)",
        "signed": "BOOLEAN",
        "order_id": "VARCHAR(50)",
    },
    str(entities.OrderStatusUpdate.__tablename__): {
        **default_cols,
        "user": "VARCHAR(100)",
        "old_status": "VARCHAR(100)",
        "new_status": "VARCHAR(100)",
        "order_id": "VARCHAR(50)",
    },
}


@pytest.mark.asyncio
async def test_tables_exist() -> None:
    expected_table_names = set(entities_columns.keys())
    async with async_engine.connect() as aconn:
        actual_table_names = await aconn.run_sync(
            lambda conn: inspect(conn).get_table_names()
        )
        assert not expected_table_names.difference(set(actual_table_names))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "table_name,expected_table_cols",
    entities_columns.items(),
)
async def test_table_columns(table_name, expected_table_cols) -> None:
    print(f"test_table_columns {table_name=}")
    async with async_engine.connect() as aconn:
        actual_table_columns = await aconn.run_sync(
            lambda conn: inspect(conn).get_columns(table_name)
        )
        actual_table_columns = {
            col["name"]: str(col["type"]) for col in actual_table_columns
        }
        print(f"{actual_table_columns=}\n{expected_table_cols=}")
        assert actual_table_columns == expected_table_cols


async def create_order_type(utils) -> Tuple[entities.OrderType, dict]:
    async with wrap_session() as session:
        service_v = services.OrderTypeService(session)
        fields = {"name": "test"}
        create_model = schemas.OrderTypeCreate(**fields)
        created = await service_v.create(create_model)
        await session.commit()
        return created, fields


async def create_order_type_param(utils) -> Tuple[entities.OrderTypeParam, dict]:
    async with wrap_session() as session:
        service_v = services.OrderTypeParamService(session)
        fields = {
            "name": "test",
            "required": True,
            "value_type": schemas.OrderParamValueType.INT,
        }
        create_model = schemas.OrderTypeParamCreate(**fields)
        order_type = await services.OrderTypeService(session).read_one()
        created = await service_v.create(create_model, order_type)
        await session.commit()
        return created, fields


async def create_order(utils) -> Tuple[entities.Order, dict]:
    async with wrap_session() as session:
        service_v = services.OrderService(session)
        user_implementer_id = await utils.get_random_user_id_order_manager()
        order_type = await services.OrderTypeService(session).read_one()
        fields = {
            "user_customer": "test",
            "user_implementer": user_implementer_id,
            "order_type_id": str(order_type.id),
            "parent_order_id": None,
        }
        create_model = schemas.OrderCreate(**fields)
        created = await service_v.create(create_model, order_type)
        await session.commit()
        return created, fields


async def create_order_param(utils) -> Tuple[entities.OrderParamValue, dict]:
    async with wrap_session() as session:
        service_v = services.OrderParamValueService(session)
        fields = {"value": "1"}
        create_model = schemas.OrderParamValueCreate(**fields)
        order_type = await services.OrderTypeService(session).read_one()
        order_type_param = await services.OrderTypeParamService(session).create(
            schemas.OrderTypeParamCreate(
                name="test1", required=False, value_type=schemas.OrderParamValueType.INT
            ),
            order_type,
        )
        user_implementer_id = await utils.get_random_user_id_order_manager()
        fields_order = {
            "user_customer": "test",
            "user_implementer": user_implementer_id,
            "order_type_id": str(order_type.id),
            "parent_order_id": None,
        }
        order = await services.OrderService(session).create(
            schemas.OrderCreate(**fields_order), order_type
        )
        created = await service_v.create(create_model, order, order_type_param)
        await session.commit()
        return created, fields


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "service,create_f",
    [
        (services.OrderTypeService, create_order_type),
        (services.OrderTypeParamService, create_order_type_param),
        (services.OrderService, create_order),
        (services.OrderParamValueService, create_order_param),
    ],
)
async def test_create_get(utils, service, create_f) -> None:
    created, fields = await create_f(utils)
    print(f"{created=}")

    async with wrap_session() as session:
        service_v = service(session)
        got = await service_v.read_one(id=str(created.id))
        assert str(got.id) == str(created.id)
        for k, v in fields.items():
            assert str(getattr(got, k)) == str(v)

    async with wrap_session() as session:
        service_v = service(session)
        items = await service_v.read_many()
        assert len(items) > 0
        assert got.id in [it.id for it in items]
