# https://fastapi.tiangolo.com/tutorial/testing/
from typing import List

import pytest
from httpx import AsyncClient

from app.core.keycloak import get_service_client
from app.schemas.order import OrderStatus

# client = TestClient(app)
base_url = "http://localhost:5010"


async def login():
    keycloak = get_service_client()
    token = await keycloak.get_token_by_secret()
    return token


@pytest.mark.asyncio
async def test_healthcheck():
    async with AsyncClient() as ac:
        response = await ac.get(f"{base_url}/version/")
    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}


@pytest.mark.asyncio
async def test_3_1_6_user_can_create_order():
    token = await login()
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3
        order_type_id = response.json()["results"][0]["id"]
        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": order_type_id,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"


@pytest.mark.asyncio
async def test_3_1_7_user_can_create_wood_request():
    token = await login()
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
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": order_type_id,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"


@pytest.mark.asyncio
async def test_3_1_13_user_can_create_defect_request():
    token = await login()
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3
        order_type_id = response.json()["results"][0]["id"]
        request_type_id = response.json()["results"][1]["id"]
        defect_type_id = response.json()["results"][2]["id"]

        response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": order_type_id,
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": request_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": defect_type_id,
                "parent_order_id": response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"


@pytest.mark.asyncio
async def test_3_1_17_user_can_filter_requests():
    token = await login()
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 3
        order_type_id = response.json()["results"][0]["id"]

        for i in range(10):
            response = await ac.post(
                f"{base_url}/api/order_type/{order_type_id}/order/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                    "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                    "order_type_id": order_type_id,
                },
            )
            assert response.status_code == 200
            assert response.json()["status"] == "NEW"

        filter_response = await ac.get(
            f"{base_url}/api/order/",
            headers={"Authorization": f"Bearer {token}"},
            params={"status": ["NEW"], "limit": 8, "order_type_id": order_type_id},
        )
        print(filter_response.json())
        assert filter_response.status_code == 200
        assert len(filter_response.json()["results"]) == 8


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
    new_statuses_updates: List[str],
):
    token = await login()
    async with AsyncClient() as ac:
        response = await ac.get(
            f"{base_url}/api/order_type/", headers={"Authorization": f"Bearer {token}"}
        )
        print(response.json())
        assert response.status_code == 200
        assert response.json()["count"] == 3
        order_type_id = response.json()["results"][0]["id"]
        request_type_id = response.json()["results"][1]["id"]

        order_response = await ac.post(
            f"{base_url}/api/order_type/{order_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": order_type_id,
            },
        )
        assert order_response.status_code == 200
        assert order_response.json()["status"] == "NEW"

        order_param_type_ids = [
            x["id"] for x in response.json()["results"][1]["params"]
        ]

        response = await ac.post(
            f"{base_url}/api/order_type/{request_type_id}/order/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "user_customer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "user_implementer": "362583d6-fa4d-454a-99e8-0fcec57706a2",
                "order_type_id": request_type_id,
                "parent_order_id": order_response.json()["id"],
            },
        )
        assert response.status_code == 200
        assert response.json()["status"] == "NEW"

        for param_id in order_param_type_ids:
            param_response = await ac.post(
                f"{base_url}/api/order_type/{request_type_id}/order/{response.json()['id']}/params/{param_id}/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "value": "1",
                },
            )
            assert param_response.status_code == 200

        for new_status in new_statuses_updates:
            update_response = await ac.put(
                f"{base_url}/api/order_type/{request_type_id}/order/{response.json()['id']}/",
                headers={"Authorization": f"Bearer {token}"},
                json={"status": new_status},
            )
            print(update_response.json())
            assert update_response.status_code == 200
            assert update_response.json()["status"] == new_status
