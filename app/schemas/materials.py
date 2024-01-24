from pydantic import BaseModel

from .util import StrEnum, TimestampedWithId


class MaterialValueType(StrEnum):
    VOLUME = "VOLUME"
    PIECE = "PIECE"
    MASS = "MASS"


class MaterialCreate(BaseModel):
    name: str
    amount: int
    value_type: MaterialValueType
    item_price: int


class MaterialUpdate(MaterialCreate):
    pass


class Material(TimestampedWithId):
    name: str
    amount: int
    value_type: MaterialValueType
    item_price: int
    user_creator: str
    user_updator: str
    order_id: str
