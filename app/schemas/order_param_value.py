from pydantic import BaseModel

from .util import TimestampedWithId


class OrderParamValueCreate(BaseModel):
    value: str


class OrderParamValueUpdate(BaseModel):
    value: str


class OrderParamValue(TimestampedWithId):
    value: str
    order_type_param_id: str
    order_id: str
