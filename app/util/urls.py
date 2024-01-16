from typing import Dict, List, Union
from urllib.parse import parse_qs, urlencode

from starlette.datastructures import URL

UrlQueryParam = Union[str, List[str]]
UrlQueryDict = Dict[str, UrlQueryParam]


def parse_query_dict(url: URL) -> UrlQueryDict:
    return {k: (v if len(v) > 1 else v[0]) for k, v in parse_qs(url.query).items()}


def dict_to_query(d: UrlQueryDict) -> str:
    return urlencode(d, doseq=True)


def replace_query_params(url: URL, **kwargs: UrlQueryParam) -> URL:
    d = parse_query_dict(url)
    to_update = {
        k: [str(it) for it in v] if isinstance(v, list) else [str(v)]
        for k, v in kwargs.items()
    }
    d.update(to_update)
    return url.replace(query=dict_to_query(d))
