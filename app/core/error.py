from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Union

from app.core import message


@dataclass
class ItemNotFound(Exception):
    item: str = "Item"

    def __str__(self) -> str:
        return message.ERROR_ENTITY_ENTRY_NOT_FOUND.format(entity=self.item)


@dataclass
class EntityEntryAlreadyExists(Exception):
    entity: str = "Item"

    def __str__(self) -> str:
        return message.ERROR_ENTITY_ENTRY_ALREADY_EXISTS.format(entity=self.entity)


@dataclass
class IncorrectSorting(Exception):
    fields: Union[List, Set, str] = ""
    with_format: bool = False
    available: Optional[Set[str]] = None

    def __str__(self) -> str:
        if self.with_format:
            return message.ERROR_INCORRECT_SORTING_WITH_FORMAT.format(
                fields=self.fields
            )
        if self.available is not None:
            return message.ERROR_INCORRECT_SORTING_WITH_AVAILABLE.format(
                fields=list(self.fields), available=list(self.available)
            )
        return message.ERROR_INCORRECT_SORTING.format(fields=self.fields)


@dataclass
class IncorrectDataFormat(Exception):
    allowed_formats: Optional[Iterable] = None
    format: Optional[Iterable] = None

    def __str__(self) -> str:
        return message.ERROR_INCORRECT_DATA_FORMAT.format(
            format=self.format or "Format",
            formats=tuple(set(self.allowed_formats or [])) or "",
        )


@dataclass
class ActionForbidden(Exception):
    def __str__(self) -> str:
        return message.ERROR_ACTION_FORBIDDEN


@dataclass
class Unauthorized(Exception):
    def __str__(self) -> str:
        return message.ERROR_NOT_AUTHORIZED
