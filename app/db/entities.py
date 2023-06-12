import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from .base_class import Base


class TimeStamped(Base):
    __abstract__ = True
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        default=func.now(),
        server_default=func.now()
    )
    updated_at = sa.Column(
        sa.DateTime(timezone=True),
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now()
    )


class TimeStampedWithId(TimeStamped):
    __abstract__ = True
    id = sa.Column(
        sa.String(36),
        primary_key=True,
        index=True,
        default=lambda: str(uuid.uuid4())
    )


DefaultSortingFields = {'id', 'updated_at', 'created_at'}


class OrderType(TimeStampedWithId):
    name = sa.Column(sa.String(100))


OrderTypeSortingFields = {*DefaultSortingFields, 'name'}


class OrderTypeParam(TimeStampedWithId):
    # TODO: add unique constraint for name + order_type_id
    name = sa.Column(sa.String(100))
    value_type = sa.Column(sa.String(100))
    required = sa.Column(sa.Boolean)
    order_type: Mapped[OrderType] = relationship('OrderType', cascade="all,delete")
    order_type_id = sa.Column(sa.String(50), sa.ForeignKey('order_type.id'), nullable=False)


OrderTypeParamSortingFields = {*DefaultSortingFields, 'name', 'value_type', 'required', 'order_type_id'}


class Order(TimeStampedWithId):
    status = sa.Column(sa.String(100))
    user_customer = sa.Column(sa.String(100))
    user_implementer = sa.Column(sa.String(100))
    order_type: Mapped[OrderType] = relationship('OrderType', cascade="all,delete")
    order_type_id = sa.Column(sa.String(50), sa.ForeignKey('order_type.id'), nullable=False)


OrderSortingFields = {*DefaultSortingFields, 'status', 'order_type_id'}


class OrderParamValue(TimeStampedWithId):
    # TODO: add unique constraint for order_id + order_type_param_id
    value = sa.Column(sa.String(100))
    order_type_param: Mapped[OrderType] = relationship('OrderTypeParam', cascade="all,delete")
    order_type_param_id = sa.Column(sa.String(50), sa.ForeignKey('order_type_param.id'), nullable=False)
    order: Mapped[Order] = relationship('Order', cascade="all,delete")
    order_id = sa.Column(sa.String(50), sa.ForeignKey('order.id'), nullable=False)


OrderParamValueSortingFields = {*DefaultSortingFields, 'value', 'order_type_param_id', 'order_id'}


class OrderConfirmation(TimeStampedWithId):
    user = sa.Column(sa.String(100))
    signed = sa.Column(sa.Boolean)
    order: Mapped[Order] = relationship('Order', cascade="all,delete")
    order_id = sa.Column(sa.String(50), sa.ForeignKey('order.id'), nullable=False)


OrderConfirmationSortingFields = {*DefaultSortingFields, 'signed', 'order_id'}
