import uuid

import sqlalchemy as sa
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


class Task(TimeStampedWithId):
    content = sa.Column(sa.String(100))


TaskSortingFields = {*DefaultSortingFields, 'content'}
