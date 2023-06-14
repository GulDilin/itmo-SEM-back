from typing import List
from pydantic import BaseModel

from app.core.error import ActionForbidden


class User(BaseModel):
    name: str
    roles: List[str]

    def raise_has_role(self):
        raise ActionForbidden('User does not have proper role')
