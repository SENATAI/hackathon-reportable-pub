import contextlib
import uuid
import re
from collections.abc import Iterable, Sequence
from typing import Any, Generic, Protocol, TypeVar, cast, get_args
from typing_extensions import Self
import sqlalchemy as sa
from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import func
from sqlalchemy.exc import IntegrityError

from ..db import Base
from ..utils.exceptions import ModelNotFoundException, SortingFieldNotFoundError, ModelAlreadyExistsError

from shared.schemas.base import CreateBaseModel, PaginationResultSchema, PaginationSchema, UpdateBaseModel

ModelType = TypeVar('ModelType', bound=Base, covariant=True)
ReadSchemaType = TypeVar('ReadSchemaType', bound=BaseModel)
CreateSchemaType = TypeVar('CreateSchemaType', bound=CreateBaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=UpdateBaseModel)


class BaseRepositoryProtocol(Protocol[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]):
    async def get(self: Self, id: uuid.UUID) -> ReadSchemaType:
        ...

    async def get_or_none(self: Self, id: uuid.UUID) -> ReadSchemaType | None:
        ...

    async def get_by_ids(self: Self, ids: Sequence[uuid.UUID]) -> list[ReadSchemaType]:
        ...

    async def get_all(self: Self) -> list[ReadSchemaType]:
        ...

    async def paginate(
        self: Self,
        search: str,
        search_by: Iterable[str],
        sorting: Iterable[str],
        pagination: PaginationSchema,
        user: Any,
        policies: list[str],
    ) -> PaginationResultSchema[ReadSchemaType]:
        ...

    async def create(self: Self, create_object: CreateSchemaType) -> ReadSchemaType:
        ...

    async def bulk_create(self: Self, create_objects: list[CreateSchemaType]) -> list[ReadSchemaType]:
        ...

    async def update(self: Self, update_object: UpdateSchemaType) -> ReadSchemaType:
        ...

    async def bulk_update(self: Self, update_objects: list[UpdateSchemaType]) -> None:
        ...

    async def upsert(self: Self, create_object: CreateSchemaType) -> ReadSchemaType:
        ...

    async def delete(self: Self, id: uuid.UUID) -> bool:
        ...


class BaseRepositoryImpl(Generic[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]):
    __orig_bases__: 'tuple[type[BaseRepositoryImpl[ModelType, ReadSchemaType, CreateSchemaType, UpdateSchemaType]]]'

    model_type: type[ModelType]
    read_schema_type: type[ReadSchemaType]

    def __init__(self, session: AsyncSession):
        """
        Base CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.session = session

    def __init_subclass__(cls) -> None:
        if not hasattr(cls, '__orig_bases__'):
            raise ValueError('Repository must be implements by BaseImplRepository')
        base_repository_generic, *_ = cls.__orig_bases__  # type: ignore
        cls.model_type, cls.read_schema_type, *_ = cast(
            tuple[type[ModelType], type[ReadSchemaType], type[CreateSchemaType], type[UpdateSchemaType]],
            get_args(base_repository_generic),
        )
        return super().__init_subclass__()

    async def get(self: Self, id: uuid.UUID) -> ReadSchemaType:
        async with self.session as s:
            statement = sa.select(self.model_type).where(self.model_type.id == id)
            model = (await s.execute(statement)).scalar_one_or_none()
            if model is None:
                raise ModelNotFoundException(self.model_type, id)
            return self.read_schema_type.model_validate(model, from_attributes=True)

    async def get_or_none(self: Self, id: uuid.UUID) -> ReadSchemaType | None:
        with contextlib.suppress(ModelNotFoundException):
            return await self.get(id)
        return None

    async def get_by_ids(self: Self, ids: Sequence[uuid.UUID]) -> list[ReadSchemaType]:
        async with self.session as s:
            statement = sa.select(self.model_type).where(self.model_type.id.in_(ids))
            models = (await s.execute(statement)).scalars().all()
            return [self.read_schema_type.model_validate(model, from_attributes=True) for model in models]

    async def get_all(self: Self) -> list[ReadSchemaType]:
        async with self.session as s:
            statement = sa.select(self.model_type)
            models = (await s.execute(statement)).scalars().all()
            return [self.read_schema_type.model_validate(model, from_attributes=True) for model in models]

    async def paginate(
        self: Self,
        search: str,
        search_by: Iterable[str],
        sorting: Iterable[str],
        pagination: PaginationSchema,
        user: Any,
        policies: list[str],
    ) -> PaginationResultSchema[ReadSchemaType]:
        if len(policies) == 0:
            return PaginationResultSchema(objects=[], count=0)
        async with self.session as s:
            statement = sa.select(self.model_type)
            if search:
                search_where: sa.ColumnElement[Any] = sa.false()
                for sb in search_by:
                    column = getattr(self.model_type, sb)
                    # Для ENUM используем точное сравнение
                    if hasattr(column, 'type') and isinstance(column.type, sa.Enum):
                        search_where = sa.or_(search_where, column == search)
                    else:
                        search_where = sa.or_(search_where, column.ilike(f'%{search}%'))
                statement = statement.where(search_where)
            order_by_expr = self.get_order_by_expr(sorting)
            models = (
                (await s.execute(statement.limit(pagination.limit).offset(pagination.offset).order_by(*order_by_expr)))
                .scalars()
                .all()
            )
            objects = [self.read_schema_type.model_validate(model, from_attributes=True) for model in models]
            count_statement = statement.with_only_columns(func.count(self.model_type.id))
            count = (await s.execute(count_statement)).scalar_one()
            return PaginationResultSchema(count=count, objects=objects)
    
    
    
    async def create(self, create_object: CreateSchemaType) -> ReadSchemaType:
        """Create single record"""
        try:
            async with self.session as s, s.begin():
                stmt = (
                    sa.insert(self.model_type)
                    .values(**create_object.model_dump(exclude={'id'}))
                    .returning(self.model_type)
                )
                model = (await s.execute(stmt)).scalar_one()
                return self.read_schema_type.model_validate(model, from_attributes=True)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                field_name = self._extract_field_name(str(e), type(create_object))
                raise ModelAlreadyExistsError(self.model_type, field_name, f"duplicate key for field: {field_name}")
            raise

    async def bulk_create(self, create_objects: list[CreateSchemaType]) -> list[ReadSchemaType]:
        if len(create_objects) == 0:
            return []
        async with self.session as s, s.begin():
            statement = sa.insert(self.model_type).returning(self.model_type)
            models = (await s.scalars(statement, [x.model_dump() for x in create_objects])).all()
            return [self.read_schema_type.model_validate(model, from_attributes=True) for model in models]

    async def update(self: Self, update_object: UpdateSchemaType) -> ReadSchemaType:
        try:
            async with self.session as s, s.begin():
                pk = update_object.id
                statement = (
                    sa.update(self.model_type)
                    .where(self.model_type.id == pk)
                    .values(update_object.model_dump(exclude={'id'}, exclude_unset=True))
                    .returning(self.model_type)
                )
                model = (await s.execute(statement)).scalar_one_or_none()
                if model is None:
                    raise ModelNotFoundException(self.model_type, pk)

                return self.read_schema_type.model_validate(model, from_attributes=True)
        except IntegrityError as e:
            if "unique constraint" in str(e).lower() or "duplicate key" in str(e).lower():
                field_name = self._extract_field_name(str(e), type(update_object))
                raise ModelAlreadyExistsError(self.model_type, field_name, f"duplicate key for field: {field_name}")

            raise


    async def bulk_update(self, update_objects: list[UpdateSchemaType]) -> None:
        if len(update_objects) == 0:
            return
        async with self.session as s, s.begin():
            statement = sa.update(self.model_type)
            await s.execute(statement, [x.model_dump(exclude_unset=True) for x in update_objects])

    async def upsert(self: Self, create_object: CreateSchemaType) -> ReadSchemaType:
        async with self.session as s, s.begin():
            primary_keys = [key.name for key in sa.inspect(self.model_type).primary_key]
            statement = (
                insert(self.model_type)
                .values(**create_object.model_dump())
                .on_conflict_do_update(
                    index_elements=primary_keys, set_=create_object.model_dump(exclude={*primary_keys})
                )
                .returning(self.model_type)
            )
            model = (await s.execute(statement)).scalar_one()
            return self.read_schema_type.model_validate(model, from_attributes=True)

    async def delete(self: Self, id: uuid.UUID) -> bool:
        async with self.session as s, s.begin():
            statement = sa.delete(self.model_type).where(self.model_type.id == id)
            await s.execute(statement)
            return True

    def get_order_by_expr(self: Self, sorting: Iterable[str]) -> list[sa.UnaryExpression]:
        order_by_expr: list[sa.UnaryExpression] = []
        for st in sorting:
            try:
                if st[0] == '-':
                    order_by_expr.append(getattr(self.model_type, st[1:]).desc())
                else:
                    order_by_expr.append(getattr(self.model_type, st))
            except AttributeError as attribute_error:
                raise SortingFieldNotFoundError(st) from attribute_error
        return order_by_expr
    
    def _extract_field_name(self, error_message: str, create_schema_type: type[CreateSchemaType]) -> str:
        """Extract field name from PostgreSQL error message"""
        
        # Паттерн для PostgreSQL: Key (email)=(value) already exists
        key_pattern = r'Key \((\w+)\)='
        match = re.search(key_pattern, error_message, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        return "field_name"  