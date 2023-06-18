from starlette.datastructures import URL

from app.schemas.util import PaginatedResponse, PaginationData
from app.settings import settings
from app.util import urls


async def get_paginated_response(
    paginated_response: PaginatedResponse,
    paginator: PaginationData,
) -> PaginatedResponse:
    url = URL(str(paginator.request.url))
    query = urls.parse_query_dict(url)
    if settings.FORCE_HTTPS:
        url = url.replace(scheme="https")
    if paginator.offset >= paginator.limit:
        query['limit'] = str(paginator.limit)
        query['offset'] = str(paginator.offset - paginator.limit)
        paginated_response.previous = str(urls.replace_query_params(url, **query))
    offset = paginator.offset + paginator.limit
    if offset < paginated_response.count:
        query['limit'] = str(paginator.limit)
        query['offset'] = str(offset)
        paginated_response.next = str(urls.replace_query_params(url, **query))
    return paginated_response
