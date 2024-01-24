from typing import Optional

from pydantic import BaseModel

from .util import StrEnum, TimestampedWithId


class OrderParamValueType(StrEnum):
    INT = "int"
    STR = "string"
    TEXT = "text"
    DATE = "date"


class OrderTypeParamCreate(BaseModel):
    name: str
    required: bool
    value_type: OrderParamValueType


class OrderTypeParamUpdate(BaseModel):
    name: Optional[str] = None
    required: Optional[bool] = None
    value_type: Optional[OrderParamValueType] = None


class OrderTypeParam(TimestampedWithId):
    name: str
    required: bool
    value_type: str
    order_type_id: str
