# https://fastapi.tiangolo.com/tutorial/testing/
import asyncio
import os
from typing import List

import pytest
from dotenv import load_dotenv
from httpx import AsyncClient

from app.api.endpoints.order import create_order, test_get_orders, update_order
from app.api.endpoints.order_param_value import create_order_type
from app.core.keycloak import get_service_client
from app.db.session import wrap_session
from app.schemas.keycloak_user import User
from app.schemas.order import OrderCreate, OrderStatus, OrderUpdate
from app.schemas.order_param_value import OrderParamValueCreate
from app.schemas.util import SortingList, SortingListItem, SortingType
from app.services.order import OrderService
from app.services.order_param_value import OrderParamValueService
from app.services.order_status_update import OrderStatusUpdateService
from app.services.order_type import OrderTypeService

load_dotenv()

# client = TestClient(app)
base_url = os.getenv('TEST_BASE_URL', "http://localhost:5010")
admin_id = ""


async def admin_login():
    keycloak = get_service_client()
    admin_token = await keycloak.get_token_by_secret()
    return admin_token


async def customer_login(utils):
    customer_token = await utils.auth_test_client()
    return customer_token


async def setup():
    kc = get_service_client()
    user = await kc.get_user_by_username("service-account-service-client")
    admin_id = user["id"]
    print(admin_id)


asyncio.run(setup())


@pytest.mark.asyncio
async def test_3_1_5_customer_cannot_view_requests(utils):
    token = await admin_login()
    consumer_token = await customer_login(utils)

    kc = get_service_client()
    user = await kc.get_user_by_username("service-account-service-client")
    admin_id = user["id"]
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3
        order_type_id = response.json()["results"][0]["id"]
        request_type_id = response.json()["results"][1]["id"]

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        response = await ac.get(
            f"{base_url}/api/order_type/{request_type_id}/order/{response.json()['id']}/",
            headers={"Authorization": f"Bearer {consumer_token}"},
        )
        print(response.json())
        assert response.status_code == 403


@pytest.mark.asyncio
async def test_3_1_6_user_can_create_order():
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)

        order_type = await service_type.read_one(dep_type="MAIN")

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=order_type.id,
        )

        response = await create_order(
            create_order_args,
            order_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
        )
    assert response.status == "NEW"


@pytest.mark.asyncio
async def test_3_1_7_user_can_create_wood_request():
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)

        order_type = await service_type.read_one(dep_type="MAIN")
        request_type = await service_type.read_one(dep_type="DEPEND")

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=order_type.id,
        )

        response = await create_order(
            create_order_args,
            order_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
        )
        assert response.status == "NEW"

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=request_type.id,
            parent_order_id=str(response.id),
        )
        response = await create_order(
            create_order_args,
            request_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
        )
    assert response.status == "NEW"


@pytest.mark.asyncio
async def test_3_1_13_user_can_create_defect_request():
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)

        order_type = await service_type.read_one(dep_type="MAIN")
        request_type = await service_type.read_one(dep_type="DEPEND")
        defect_type = await service_type.read_one(dep_type="DEFECT")

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=order_type.id,
        )

        response = await create_order(
            create_order_args,
            order_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
        )
        assert response.status == "NEW"

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=request_type.id,
            parent_order_id=str(response.id),
        )
        response = await create_order(
            create_order_args,
            request_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
        )
        assert response.status == "NEW"

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=defect_type.id,
            parent_order_id=str(response.id),
        )
        response = await create_order(
            create_order_args,
            defect_type,
            service_v,
            user=User(
                user_id=admin_id,
                name="name",
                roles=["staff_order_manager", "staff_customer_manager", "STAFF"],
            ),
        )
    assert response.status == "NEW"


@pytest.mark.asyncio
async def test_3_1_17_user_can_filter_requests():
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)

        order_type = await service_type.read_one(dep_type="MAIN")

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=order_type.id,
        )
        for i in range(10):
            response = await create_order(
                create_order_args,
                order_type,
                service_v,
                user=User(
                    user_id=admin_id,
                    name="name",
                    roles=["1", "staff_customer_manager", "STAFF"],
                ),
            )
            assert response.status == "NEW"
        filter_response = await test_get_orders(
            order_type=order_type,
            order_service=service_v,
            user_data=User(
                user_id=admin_id,
                name="name",
                roles=["1", "staff_customer_manager", "STAFF"],
            ),
            filter_data={"status": ["NEW"], "limit": 8, "order_type_id": order_type.id},
            sorting_list=SortingList(
                sorting_list=[SortingListItem(type=SortingType.ASC, field="id")]
            ),
        )

        assert len(filter_response.results) == 8


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "new_statuses_updates",
    [
        ([OrderStatus.READY]),
        (
            [
                OrderStatus.READY,
                OrderStatus.IN_PROGRESS,
                OrderStatus.DONE,
                OrderStatus.ACCEPTED,
            ]
        ),
        (
            [
                OrderStatus.READY,
                OrderStatus.IN_PROGRESS,
                OrderStatus.DONE,
                OrderStatus.READY,
            ]
        ),
        (
            [
                OrderStatus.READY,
                OrderStatus.IN_PROGRESS,
                OrderStatus.DONE,
                OrderStatus.READY,
                OrderStatus.IN_PROGRESS,
                OrderStatus.DONE,
                OrderStatus.ACCEPTED,
            ]
        ),
    ],
)
async def test_3_1_20_user_can_change_status_of_any_request(
    new_statuses_updates: List[OrderStatus],
):
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)
        service_param = OrderParamValueService(session)
        service_status_update = OrderStatusUpdateService(session)

        order_type = await service_type.read_one(dep_type="MAIN")
        request_type = await service_type.read_one(dep_type="DEPEND")

        user = User(
            user_id=admin_id,
            name="name",
            roles=["1", "staff_customer_manager", "STAFF", "staff_order_manager"],
        )

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=order_type.id,
        )
        order = await create_order(
            create_order_args,
            order_type,
            service_v,
            user=user,
        )
        assert order.status == "NEW"

        create_order_args = OrderCreate(
            user_customer=admin_id,
            user_implementer=admin_id,
            order_type_id=request_type.id,
            parent_order_id=str(order.id),
        )
        response = await create_order(
            create_order_args,
            request_type,
            service_v,
            user,
        )
        assert response.status == "NEW"

        for param in request_type.params:
            print(f"Setting {param.name}")
            result = await create_order_type(
                OrderParamValueCreate(value="1"),
                await service_v.read_one(id=str(response.id)),
                param,
                order_param_value_service=service_param,
                user_data=user,
            )
            print(result)
        await session.commit()
    async with wrap_session() as session:
        service_v = OrderService(session)
        service_type = OrderTypeService(session)
        service_status_update = OrderStatusUpdateService(session)
        for new_status in new_statuses_updates:
            request = await service_v.read_one(
                id=str(response.id),
                load_props=["params"],
            )
            print(request.params)
            new_order = await update_order(
                OrderUpdate(status=new_status),
                request,
                request_type,
                service_type,
                service_v,
                service_status_update,
                user,
            )
            assert new_order.status == new_status
