from typing import List, Optional

from pydantic import BaseModel

from .order_type_param import OrderTypeParam
from .util import StrEnum, TimestampedWithId


class OrderTypeName(StrEnum):
    BATH_ORDER = "Заказ на баню"
    TIMBER_ORDER = "Заявка на сруб"
    DEFECT_ORDER = "Заявка на брак"
    DELIVERY_ORDER = "Заявка на доставку"
    MAGIC_ORDER = "Заявка на зачарование"
    CRAFT_PRODUCT_ORDER = "Заявка на изделие ремесленника"


class OrderDepType(StrEnum):
    MAIN = 'MAIN'
    DEPEND = 'DEPEND'
    DEFECT = 'DEFECT'
    DELIVERY = 'DELIVERY'


class OrderTypeCreate(BaseModel):
    name: str
    dep_type: str


class OrderTypeUpdate(BaseModel):
    name: str


class OrderType(TimestampedWithId):
    name: str
    dep_type: Optional[str]
    params: List[OrderTypeParam]
