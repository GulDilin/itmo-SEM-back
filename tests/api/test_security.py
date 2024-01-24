# https://fastapi.tiangolo.com/tutorial/testing/
from typing import List

import pytest
from httpx import AsyncClient

from app.core.keycloak import get_service_client
from app.schemas.order import OrderStatus

# client = TestClient(app)
base_url = "http://localhost:5010"


async def admin_login():
    keycloak = get_service_client()
    admin_token = await keycloak.get_token_by_secret()
    return admin_token


async def setup():
    admin_token = await admin_login()
    kc = get_service_client()
    user = await kc.get_user_by_username("service-account-service-client")
    admin_id = user["id"]
    return admin_token, admin_id


async def customer_login(utils):
    customer_token = await utils.auth_test_client()
    return customer_token


async def get_order_id(admin_token, name, ac):
    response = await ac.get(
        f"{base_url}/api/order_type/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    result_order = {}
    for i in response.json()["results"]:
        if i["name"] == name:
            result_order = i
    return result_order["id"]


async def assign_roles_to_test_user(utils, roles: List[str]) -> str:
    kc = get_service_client()
    test_user = await kc.get_user_by_username("service-account-test-client")
    test_user_id = test_user["id"]
    await kc.clear_user_roles(test_user_id)
    await kc.add_user_roles(
        test_user_id, [await kc.get_role_by_name(role_name=it) for it in roles]
    )
    return await customer_login(utils)


async def fill_all_order_values(type_id, order_id, admin_token, ac):
    response = await ac.get(
        f"{base_url}/api/order_type/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    result_order = None
    for i in response.json()["results"]:
        if i["id"] == type_id:
            result_order = i
    order_param_type_ids = [x["id"] for x in result_order["params"]]

    for param_id in order_param_type_ids:
        param_response = await ac.post(
            f"{base_url}/api/order_type/{type_id}/order/{order_id}/params/{param_id}/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "value": "1",
            },
        )
        assert param_response.status_code == 200


@pytest.mark.asyncio
async def test_security_healthcheck(utils):
    async with AsyncClient() as ac:
        response = await ac.get(f"{base_url}/version/")
    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}
    token = await assign_roles_to_test_user(utils, ["staff"])
    print(token)
    assert token != ""


@pytest.mark.parametrize(
    "user_roles",
    [
        (["customer"]),
        (["user"]),
        (["customer", "user"]),
    ],
)
@pytest.mark.asyncio
async def test_customer_can_only_view_orders(utils, user_roles: List[str]):
    admin_token, admin_id = await setup()
    token = await assign_roles_to_test_user(utils, user_roles)

    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 6
        order_type_id = await get_order_id(admin_token, "Заказ на баню", ac)
        request_type_id = await get_order_id(admin_token, "Заявка на сруб", ac)

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        print(response.json())
        assert response.status_code == 403

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        print(response.json())
        order_id = response.json()["id"]
        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )

        filter_response = await ac.get(
            f"{base_url}/api/order/{response.json()['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(filter_response.content)
        assert filter_response.status_code == 307

        update_response = await ac.put(
            f"{base_url}/api/order_type/{order_type_id}/order/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "READY"},
        )
        print(update_response.content)
        assert update_response.status_code == 307

        delete_response = await ac.delete(
            f"{base_url}/api/order_type/{order_type_id}/order/{order_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(delete_response.content)
        assert delete_response.status_code == 307


@pytest.mark.parametrize(
    "user_roles",
    [
        (["customer"]),
        (["user"]),
        (["customer", "user"]),
    ],
)
@pytest.mark.asyncio
async def test_customer_cannot_work_with_requests(utils, user_roles: List[str]):
    admin_token, admin_id = await setup()
    token = await assign_roles_to_test_user(utils, user_roles)

    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 6

        order_type_id = await get_order_id(admin_token, "Заказ на баню", ac)
        request_type_id = await get_order_id(admin_token, "Заявка на сруб", ac)

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        print(response.json())
        order_id = response.json()["id"]
        await fill_all_order_values(order_type_id, order_id, admin_token, ac)

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": order_id,
            },
        )
        request_id = response.json()["id"]

        filter_response = await ac.get(
            f"{base_url}/api/order/{request_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(filter_response.content)
        assert filter_response.status_code == 307

        update_response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        print(update_response.content)
        assert update_response.status_code == 403

        update_response = await ac.put(
            f"{base_url}/api/order_type/{request_type_id}/order/{request_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "READY"},
        )
        print(update_response.content)
        assert update_response.status_code == 307

        delete_response = await ac.delete(
            f"{base_url}/api/order_type/{request_type_id}/order/{request_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(delete_response.content)
        assert delete_response.status_code == 307


@pytest.mark.parametrize(
    "user_roles",
    [
        (["customer"]),
        (["user"]),
        (["customer", "user"]),
        (["staff", "user"]),
        (["staff_axeman", "staff"]),
    ],
)
@pytest.mark.asyncio
async def test_customer_cannot_work_with_defects(utils, user_roles: List[str]):
    admin_token, admin_id = await setup()
    token = await assign_roles_to_test_user(utils, user_roles)
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        assert response.json()["count"] == 6

        order_type_id = await get_order_id(admin_token, "Заказ на баню", ac)
        request_type_id = await get_order_id(admin_token, "Заявка на сруб", ac)
        defect_type_id = await get_order_id(admin_token, "Заявка на брак", ac)

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        request_id = response.json()["id"]

        response = await ac.post(
            f"{base_url}/api/order_type/{defect_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": defect_type_id,
                "parent_order_id": request_id,
            },
        )
        defect_id = response.json()["id"]

        filter_response = await ac.get(
            f"{base_url}/api/order/{defect_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(filter_response.content)
        assert filter_response.status_code == 307

        update_response = await ac.post(
            f"{base_url}/api/order_type/{defect_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": defect_type_id,
                "parent_order_id": defect_id,
            },
        )
        print(update_response.content)
        assert update_response.status_code == 403

        update_response = await ac.put(
            f"{base_url}/api/order_type/{defect_type_id}/order/{defect_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"status": "READY"},
        )
        print(update_response.content)
        assert update_response.status_code == 307

        delete_response = await ac.delete(
            f"{base_url}/api/order_type/{defect_type_id}/order/{defect_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        print(delete_response.content)
        assert delete_response.status_code == 307


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "start_statuses,new_statuses_updates,user_roles",
    [
        (
            [OrderStatus.READY],
            [OrderStatus.NEW],
            ["customer", "user", "staff", "staff_axeman", "staff_order_manager"],
        ),
        (
            [OrderStatus.READY],
            [OrderStatus.IN_PROGRESS],
            ["customer", "user", "staff", "staff_customer_manager"],
        ),
        (
            [OrderStatus.READY, OrderStatus.IN_PROGRESS],
            [OrderStatus.DONE],
            ["customer", "user", "staff", "staff_customer_manager"],
        ),
        (
            [OrderStatus.READY, OrderStatus.IN_PROGRESS, OrderStatus.DONE],
            [OrderStatus.ACCEPTED],
            ["customer", "user", "staff", "staff_axeman", "staff_customer_manager"],
        ),
    ],
)
async def test_user_cannot_change_status(
    utils,
    start_statuses: List[str],
    new_statuses_updates: List[str],
    user_roles: List[str],
):
    admin_token, admin_id = await setup()
    token = await assign_roles_to_test_user(utils, user_roles)
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        print(response.json())
        assert response.status_code == 200
        assert response.json()["count"] == 6

        order_type_id = await get_order_id(admin_token, "Заказ на баню", ac)
        request_type_id = await get_order_id(admin_token, "Заявка на сруб", ac)

        order_response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": order_type_id,
            },
        )
        assert order_response.status_code == 200
        assert order_response.json()["status"] == "NEW"

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "user_customer": admin_id,
                "user_implementer": admin_id,
                "order_type_id": request_type_id,
                "parent_order_id": order_response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        await fill_all_order_values(request_type_id, response.json()["id"], admin_token, ac)

        for new_status in start_statuses:
            update_response = await ac.put(
                f"{base_url}/api/order_type/{request_type_id}/order/{response.json()['id']}/",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"status": new_status},
            )
            print(update_response.json())
            assert update_response.status_code == 200
            assert update_response.json()["status"] == new_status

        for new_status in new_statuses_updates:
            update_response = await ac.put(
                f"{base_url}/api/order_type/{request_type_id}/order/{response.json()['id']}/",
                headers={"Authorization": f"Bearer {token}"},
                json={"status": new_status},
            )
            print(update_response.json())
            assert update_response.status_code == 403
