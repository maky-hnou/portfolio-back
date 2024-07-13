from typing import Any, TypeVar

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.base import Base
from portfolio_backend.db.dependencies import get_db_session

ModelInstance = TypeVar("ModelInstance", bound="Base")


class BaseDAO:
    """Base class for CRUD transactions."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def add_single_on_conflict_do_nothing(self, model_instance: ModelInstance) -> None:
        """Add a single model instance, do nothing on conflict."""
        await self.session.execute(
            pg_insert(model_instance.__class__).values(**model_instance.__dict__).on_conflict_do_nothing()
        )

    async def add_single_on_conflict_do_update(self, model_instance: ModelInstance, conflict_column: str) -> None:
        """Add a single model instance, update on conflict."""
        await self.session.execute(
            pg_insert(model_instance.__class__)
            .values(**model_instance.__dict__)
            .on_conflict_do_update(index_elements=[conflict_column], set_=model_instance.__dict__)
        )

    async def add_many_on_conflict_do_nothing(self, model_instances: list[ModelInstance]) -> None:
        """Add multiple model instances, do nothing on conflict."""
        if model_instances:
            await self.session.execute(
                pg_insert(model_instances[0].__class__)
                .values([instance.__dict__ for instance in model_instances])
                .on_conflict_do_nothing()
            )

    async def add_many_on_conflict_do_update(self, model_instances: list[ModelInstance], conflict_column: str) -> None:
        """Add multiple model instances, update on conflict."""
        if model_instances:
            insert_stmt = pg_insert(model_instances[0].__class__).values(
                [instance.__dict__ for instance in model_instances]
            )
            update_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[conflict_column],
                set_={k: insert_stmt.excluded[k] for k in model_instances[0].__dict__.keys()},  # noqa SIM118
            )
            await self.session.execute(update_stmt)

    async def get_single_row(self, model_class: type[ModelInstance], **filters: dict[str, Any]) -> ModelInstance | None:
        """Get a single row based on filters."""
        query = select(model_class).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_many_rows(
        self, model_class: type[ModelInstance], **filters: dict[str, Any]
    ) -> list[ModelInstance | None]:
        """Get multiple rows based on filters."""
        query = select(model_class).filter_by(**filters)
        result = await self.session.execute(query)
        return list(result.scalars().fetchall())

    async def get_all_rows(self, model_class: type[ModelInstance]) -> list[ModelInstance | None]:
        """Get all rows from a model's table."""
        result = await self.session.execute(select(model_class))
        return list(result.scalars().fetchall())

    async def delete_single_row(self, model_class: type[ModelInstance], **filters: dict[str, Any]) -> None:
        """Delete a single row based on filters."""
        await self.session.execute(delete(model_class).filter_by(**filters))

    async def delete_many_rows(self, model_class: type[ModelInstance], **filters: dict[str, Any]) -> None:
        """Delete multiple rows based on filters."""
        await self.session.execute(delete(model_class).filter_by(**filters))

    async def get_many_rows_by_column(
        self,
        model_class: type[ModelInstance],
        column: str,
        value: Any,
    ) -> list[ModelInstance | None]:
        """Get multiple rows based on a specific column value."""
        query = select(model_class).filter(column == value)
        result = await self.session.execute(query)
        return list(result.scalars().fetchall())
