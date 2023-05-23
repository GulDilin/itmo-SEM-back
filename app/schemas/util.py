from datetime import datetime
from enum import Enum
from typing import Any, List, Union
from uuid import UUID

from fastapi import Request
from pydantic import AnyHttpUrl, BaseModel, Field


class PaginatedResponse(BaseModel):
    results: List
    next: Union[AnyHttpUrl, str, None]
    previous: Union[AnyHttpUrl, str, None]
    count: int


class PaginationData(BaseModel):
    request: Request
    limit: int = Field(10, ge=0)
    offset: int = Field(0, ge=0)

    class Config:
        arbitrary_types_allowed = True


class Timestamped(BaseModel):
    created_at: datetime
    updated_at: datetime


class TimestampedWithId(Timestamped):
    id: UUID


class ValuesEnum(Enum):
    @classmethod
    def values(cls) -> List[Any]:
        return [it.value for it in cls]

    @classmethod
    def from_value(cls, val: Any) -> Any:
        return [it for it in cls if it.value == val][0]

    def __str__(self) -> str:
        return str(self.value)


class StrEnum(str, ValuesEnum):
    pass


class Version(BaseModel):
    version: str


class SortingType(StrEnum):
    ASC = 'ASC'
    DESC = 'DESC'


class SortingListItem(BaseModel):
    type: SortingType
    field: str


class SortingList(BaseModel):
    sorting_list: List[SortingListItem]


class DatetimeConverter(BaseModel):
    dt: datetime
