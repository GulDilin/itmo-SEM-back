from pydantic import BaseModel

from .util import TimestampedWithId


class OrderLinkCreate(BaseModel):
    order_left_id: str
    order_right_id: str
    link_type_id: str


class OrderLink(TimestampedWithId):
    order_left_id: str
    order_right_id: str
    link_type_id: str
