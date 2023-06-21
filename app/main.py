import asyncio
import traceback
from typing import Dict, Optional

import pydantic
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import schemas, services
from app.api.api import router as api_router
from app.core import error
from app.db.session import wrap_session
from app.log import logger
from app.settings import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/openapi.json",
)

app.include_router(api_router, prefix='/api')


@app.get('/health/')
async def health() -> int:
    return status.HTTP_200_OK


@app.get('/version/', response_model=schemas.Version)
async def version() -> schemas.Version:
    return schemas.Version(version=settings.VERSION)


if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def handle_default_error(exc: Exception, status_code: int, headers: Optional[Dict] = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={'detail': str(exc)},
        headers=headers
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Internal server error (500) : {traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': "Internal Server Error"},
    )


@app.exception_handler(ValueError)
@app.exception_handler(error.IncorrectDataFormat)
@app.exception_handler(error.IncorrectSorting)
@app.exception_handler(error.EntityEntryAlreadyExists)
async def client_exception_handler(req: Request, exc: Exception) -> JSONResponse:  # noqa
    logger.error(f"Bad request (400) : {traceback.format_exc()}")
    return handle_default_error(exc, status.HTTP_400_BAD_REQUEST)


@app.exception_handler(error.Unauthorized)
async def auth_exception_handler(req: Request, exc: Exception) -> JSONResponse:  # noqa
    logger.error(f"Unauthorized (401) : {traceback.format_exc()}")
    return handle_default_error(exc, status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(pydantic.error_wrappers.ValidationError)
async def pydantic_validation_error_handler(
        request: Request,  # noqa
        exc: pydantic.error_wrappers.ValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={'detail': exc.errors()},
    )


@app.exception_handler(error.ItemNotFound)
async def not_found_exception_handler(req: Request, exc: Exception) -> JSONResponse:  # noqa
    return handle_default_error(exc, status.HTTP_404_NOT_FOUND)


@app.exception_handler(error.ActionForbidden)
async def forbidden_exception_handler(req: Request, exc: Exception) -> JSONResponse:  # noqa
    logger.error(f"Forbidden (404) : {traceback.format_exc()}")
    return handle_default_error(exc, status.HTTP_403_FORBIDDEN)


async def test_job() -> None:
    from datetime import datetime, timedelta

    import pytz
    from fastapi.encoders import jsonable_encoder
    logger.info("Job started")
    async with wrap_session() as session:
        timeout = timedelta(0, 60)  # one minute
        order_service = services.OrderService(session)
        order_status_service = services.OrderStatusUpdateService(session)
        orders_to_remove = await order_service.read_many(status=schemas.OrderStatus.TO_REMOVE)
        for order in orders_to_remove:
            if order.history[-1].created_at + timeout < datetime.now(pytz.UTC):
                await order_status_service.create(
                    user=schemas.User(name="SYSTEM", user_id="SYSTEM", roles=[]),
                    new_order_status=schemas.OrderStatus.REMOVED,
                    old_order_status=schemas.OrderStatus(order.status),
                    order_id=str(order.id))
                await order_service.update(
                    id=str(order.id),
                    **jsonable_encoder(schemas.OrderUpdate(status=schemas.OrderStatus.REMOVED), exclude_none=True))
                logger.info(f"Cleared order {order.id}")
        await session.commit()
    logger.info("Job ended")


@app.on_event("startup")
async def startup_event() -> None:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler(event_loop=asyncio.get_running_loop())
    for job, interval in [
        (test_job, "* * * * *"),
    ]:
        await job()
        scheduler.add_job(job, CronTrigger.from_crontab(interval))
    scheduler.start()
