from functools import reduce
from typing import (Any, Callable, Iterable, List, Optional, Sequence, Set,
                    Type, Union)
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, delete, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Query, joinedload
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import ColumnElement

from app import schemas
from app.core import error
from app.db.base_class import Base

QueryModifier = Callable[[Query], Query]


class BaseService:
    def __init__(
        self,
        db_session: AsyncSession,
        entity: Type,
        entity_name: str,
        sorting_fields: Optional[Set[str]] = None,
    ):
        self.db_session = db_session
        self.entity = entity
        self.entity_name = entity_name
        self.sorting_fields = sorting_fields or Set[str]()

    def _set_filter_chunk(self, key: Any, value: Any) -> Any:
        if isinstance(value, bool):
            return getattr(self.entity, key).is_(value)
        if isinstance(value, list):
            return getattr(self.entity, key).in_(value)
        return getattr(self.entity, key) == value

    def _set_filter(
        self, q: Query, filtering: dict, filtering_policy: str = "and"
    ) -> Query:
        predicate = or_ if filtering_policy == "or" else and_
        return q.filter(
            predicate(*(self._set_filter_chunk(k, v) for k, v in filtering.items()))
        )

    def _parse_sorting(
        self,
        sorting: Optional[schemas.SortingList] = None,
    ) -> Optional[List[ColumnElement]]:
        """
        Convert sorting list to list of column operators

        :param sorting: SortingList with sorting fields and sorting type to use order_by
        :return: order_by list
        """
        if sorting is None:
            return None
        error_fields = {
            it.field
            for it in sorting.sorting_list
            if it.field not in self.sorting_fields
        }
        if len(error_fields) > 0:
            raise error.IncorrectSorting(
                fields=error_fields, available=self.sorting_fields
            )
        order_by = [
            getattr(self.entity, it.field).desc()
            if it.type == schemas.SortingType.DESC
            else getattr(self.entity, it.field).asc()
            for it in sorting.sorting_list
        ]
        return order_by

    @staticmethod
    def _set_order_by(
        query: Query, order_by: Optional[List[ColumnElement]] = None
    ) -> Query:
        """
        Define query ORDER BY part

        :param query: Database query
        :param order_by: List of ColumnElement (desc or asc)
        :return: Modified database query
        """
        return query.order_by(*order_by) if order_by else query

    def _set_joinedload_nested(self, q: Query, load_props: List[str]) -> Query:
        attr = getattr(
            self.entity, load_props[0]
        )  # type is sqlalchemy.orm.attributes.InstrumentedAttribute
        load = joinedload(attr)
        parent_entity = attr.property.entity.entity
        for field in load_props[1:]:
            attr = getattr(parent_entity, field)
            load = load.joinedload(attr)
            parent_entity = attr.property.entity.entity
        return q.options(load)

    def _set_joinedload(
        self, q: Query, load_props: Optional[Iterable[str]] = None
    ) -> Query:
        """
        Define fields that will be loaded with joinedload (for inner entity fields)

        :param query: Database query
        :param prefetch_fields: Iterable with field names that will be prefetched
        :return: Modified database query
        """
        if load_props is not None:
            for field in load_props:
                load_props = [it for it in field.split(".") if it]
                q = self._set_joinedload_nested(q, load_props)
        return q

    # def _set_joinedload(
    #     self,
    #     q: Query,
    #     load_props: Optional[Iterable[str]] = None
    # ) -> Query:
    #     """
    #     Define joined load modifiers (to load some foreign fields on select)

    #     :param q: Database query
    #     :param load_props: Iterable with attrs names
    #     :return: Modified database query
    #     """
    #     return reduce(
    #         lambda acc, attr: acc.options(joinedload(getattr(self.entity, attr))),
    #         load_props or [],
    #         q
    #     )

    @staticmethod
    def _set_modifiers(
        q: Query,
        modifiers: Optional[Iterable[QueryModifier]] = None,
    ) -> Query:
        """
        Define query modifiers (functions that get query as arg and return modified query)

        :param q: Database query
        :param modifiers: Iterable with query modifiers
        :return: Modified database query
        """
        return reduce(lambda acc, m: m(acc), modifiers or [], q)

    def _setup_query(
        self,
        operator: Callable = select,
        selectable: Any = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        load_props: Optional[List[str]] = None,
        filtering_policy: str = "and",
        modifiers: Optional[Iterable[QueryModifier]] = None,
        sorting_list: Optional[schemas.SortingList] = None,
        **kwargs: Any,
    ) -> Query:
        q = operator(selectable if selectable is not None else self.entity)
        q = self._set_filter(q=q, filtering=kwargs, filtering_policy=filtering_policy)
        q = self._set_joinedload(q=q, load_props=load_props)
        q = self._set_modifiers(q=q, modifiers=modifiers)
        if operator == select:
            order_by = self._parse_sorting(sorting=sorting_list)
            q = self._set_order_by(query=q, order_by=order_by)
        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return q

    async def count(
        self,
        predicate: Optional[Any] = None,
        **kwargs: Any,
    ) -> int:
        if "sorting_list" in kwargs:
            kwargs["sorting_list"] = None
        if not predicate:
            predicate = self.entity.id
        q = self._setup_query(selectable=func.count(predicate), **kwargs)
        return (await self.db_session.execute(q)).scalar_one() or 0

    async def read_many(
        self, offset: int = 0, limit: Optional[int] = None, **kwargs: Any
    ) -> Sequence[Any]:
        return (
            (
                await self.db_session.execute(
                    self._setup_query(offset=offset, limit=limit, **kwargs)
                )
            )
            .scalars()
            .unique()
            .all()
        )

    async def read_many_paginated(
        self,
        *args: Any,
        wrapper_class: Type,
        offset: int = 0,
        limit: Optional[int] = None,
        method: Optional[Callable] = None,
        **kwargs: Any,
    ) -> schemas.PaginatedResponse:
        """
        Get count of items by filter

        :param args: Args will be passed to method
        :param wrapper_class: Class that will wrap entity from database
        :param offset: Offset value for database query (skip first results amount)
        :param limit: Limit value for database query (max results amount)
        :param method: Callable method that will be used to get paginated results
        :param kwargs: Dictionary will be passed to _setup_query function
        :return: PaginatedResponse with results
        """
        if not method:
            method = self.read_many
        count = await self.count(**kwargs) or 0
        kwargs["limit"] = limit
        kwargs["offset"] = offset
        results = [
            wrapper_class(**jsonable_encoder(it))
            for it in await method(*args, **kwargs)
        ]
        return schemas.PaginatedResponse(results=results, count=count)

    async def read_one(self, **kwargs: Any) -> Any:
        if item := (
            await self.db_session.execute(self._setup_query(**kwargs))
        ).scalar():
            return item
        raise error.ItemNotFound(item=self.entity_name)

    async def exists(self, **kwargs: Any) -> bool:
        return bool(
            (await self.db_session.execute(self._setup_query(**kwargs))).scalar()
        )

    async def _create(self, item: Base) -> Any:
        try:
            self.db_session.add(item)
            await self.db_session.flush()  # noqa
            return await self.read_one(id=item.id)
        except Exception as e:
            await self.db_session.rollback()  # noqa
            raise e

    async def _update(self, id: Union[UUID, str], item: Any) -> Any:
        await self.read_one(id=id)
        q = (
            update(self.entity)
            .where(self.entity.id == id)
            .values(**jsonable_encoder(item))
            .execution_options(synchronize_session="fetch")
        )
        try:
            await self.db_session.execute(q)
            return await self.read_one(id=id)
        except Exception as e:
            await self.db_session.rollback()  # noqa
            raise e

    async def update(self, id: Union[UUID, str], **kwargs: Any) -> Any:
        return await self._update(id=id, item=kwargs)

    async def delete(self, **kwargs: Any) -> None:
        await self.db_session.execute(self._setup_query(operator=delete, **kwargs))
        await self.db_session.flush()  # noqa
