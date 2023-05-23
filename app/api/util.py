from starlette.datastructures import URL

from app.schemas.util import PaginatedResponse, PaginationData
from app.settings import settings


async def get_paginated_response(
        paginated_response: PaginatedResponse,
        paginator: PaginationData,
) -> PaginatedResponse:
    url = URL(str(paginator.request.url))
    if settings.FORCE_HTTPS:
        url = url.replace(scheme="https")
    if paginator.offset >= paginator.limit:
        paginated_response.previous = str(url.replace_query_params(
            limit=paginator.limit,
            offset=paginator.offset - paginator.limit
        ))
    offset = paginator.offset + paginator.limit
    if offset < paginated_response.count:
        paginated_response.next = str(url.replace_query_params(
            limit=paginator.limit,
            offset=offset
        ))
    return paginated_response
