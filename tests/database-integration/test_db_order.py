# https://fastapi.tiangolo.com/tutorial/testing/

from app.db.session import wrap_session
from app.db.entities import OrderType
from app import schemas
from app.services import OrderTypeService
import pytest

@pytest.mark.asyncio
async def test_create() -> None:
    async with wrap_session() as session:
        order_type_service = OrderTypeService(session)
        created = await order_type_service.create(schemas.OrderTypeCreate(name="test"))
        got = await order_type_service.read_one(id=str(created.id))
        assert got == created
