from pydantic import BaseModel

from .util import TimestampedWithId


class TaskCreate(BaseModel):
    content: str


class TaskUpdate(BaseModel):
    content: str


class Task(TimestampedWithId):
    content: str
