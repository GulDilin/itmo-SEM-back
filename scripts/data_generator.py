import asyncio
import os
import sys
from contextlib import suppress
from random import choice, randint
from string import ascii_letters, digits
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import schemas, services  # noqa
from app.db import entities  # noqa
from app.db.session import wrap_session  # noqa
from tests.conftest import Utils  # noqa


async def create_order(session, order_type: entities.OrderType) -> entities.Order:
    order_service = services.OrderService(session)
    order_type_service = services.OrderTypeService(session)
    user_implementer_id = await Utils.get_random_user_id_order_manager()
    user_custormer_id = await Utils.get_random_user_id_customer()
    order_type_main = await order_type_service.read_one(dep_type="MAIN")
    orders = await order_service.read_many(order_type_id=str(order_type_main.id))
    orders_ids = [it.id for it in orders]
    fields = {
        "user_customer": user_custormer_id,
        "user_implementer": user_implementer_id,
        "order_type_id": str(order_type.id),
        "parent_order_id": None
        if str(order_type.dep_type) == "MAIN"
        else choice(orders_ids),
    }
    print(f"{fields=}")
    create_model = schemas.OrderCreate(**fields)
    created = await order_service.create(create_model, order_type)
    return created


def generate_order_param_value(value_type: schemas.OrderParamValueType):
    if value_type == schemas.OrderParamValueType.INT:
        return randint(1, 200)
    if value_type == schemas.OrderParamValueType.STR:
        return "".join([choice(ascii_letters + digits) for _ in range(20)])
    return None


async def create_order_param(
    session, order_type: entities.OrderType, order: entities.Order
) -> List[entities.OrderParamValue]:
    order_param_service = services.OrderParamValueService(session)
    order_type_param_service = services.OrderTypeParamService(session)
    params = await order_type_param_service.read_many(order_type_id=str(order_type.id))
    created = []
    for param in params:
        value = generate_order_param_value(param.value_type)
        created.append(
            await order_param_service.create(
                schemas.OrderParamValueCreate(value=str(value)), order, param
            )
        )
    return created


async def generate(n: int):
    async with wrap_session() as session:
        order_type_service = services.OrderTypeService(session)
        order_type = await order_type_service.read_one(dep_type="MAIN")
        order = await create_order(session, order_type)
        await session.commit()

    created_n = 0
    while created_n < n:
        async with wrap_session() as session:
            order_type_service = services.OrderTypeService(session)
            order_types = await order_type_service.read_many()
            with suppress(Exception):
                order_type = choice(order_types)
                order = await create_order(session, order_type)
                await create_order_param(session, order_type, order)
                await session.commit()
                created_n += 1
                print(f"created_order {created_n}/{n}")


if __name__ == "__main__":
    main_loop = asyncio.new_event_loop()
    main_loop.run_until_complete(generate(1000))
