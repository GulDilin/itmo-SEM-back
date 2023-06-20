import re

from starlette.datastructures import URL

from app import schemas
from app.core import error
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


def parse_sorting_item(sorting_item: str) -> schemas.SortingListItem:
    field = sorting_item
    sorting_type = schemas.SortingType.ASC
    if sorting_item.startswith("-") or sorting_item.startswith("+"):
        field = field[1:]
    if sorting_item.startswith("-"):
        sorting_type = schemas.SortingType.DESC
    return schemas.SortingListItem(field=field, type=sorting_type)


def parse_sorting(sorting_str: str) -> schemas.SortingList:
    sorting_str = sorting_str.replace(' ', '')
    parts = {it for it in sorting_str.split(",") if it}
    part_regex = r'^[+-]*(\w)+$'
    matches = [re.match(part_regex, it) for it in parts]
    if None in matches:
        raise error.IncorrectSorting(fields=sorting_str, with_format=True)
    sorting_list = [parse_sorting_item(it) for it in parts]
    fields = [it.field for it in sorting_list]
    unique = set(fields)
    if len(fields) != len(unique):
        raise error.IncorrectSorting(fields='duplicates', with_format=True)
    return schemas.SortingList(sorting_list=sorting_list)
