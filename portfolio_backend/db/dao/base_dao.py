"""Module containing the BaseDAO class for database operations.

This module provides an abstract base class for performing common CRUD
(Create, Read, Update, Delete) operations on SQLAlchemy model instances
within an asynchronous FastAPI environment. It handles conflict resolution
during insertions and supports both single and batch operations.

Classes:
    BaseDAO: Base class providing utility methods for CRUD transactions.

Dependencies:
    - AsyncSession: SQLAlchemy asynchronous session, injected via FastAPI's dependency system.
"""

from typing import Any, TypeVar

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.base import Base
from portfolio_backend.db.dependencies import get_db_session

ModelInstance = TypeVar("ModelInstance", bound="Base")


class BaseDAO:
    """Base class for CRUD transactions.

    Args:
        session (AsyncSession): The asynchronous database session used for Message model transactions.
    """

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        """Initialize the BaseDAO with a database session.

        Args:
            session (AsyncSession): The database session used for transactions, injected via FastAPI's dependency system.
        """
        self.session = session

    @staticmethod
    def _get_model_data(model_instance: ModelInstance) -> dict[str, Any]:
        """Extract the column data from a model instance as a dictionary.

        Args:
            model_instance (ModelInstance): The instance of the SQLAlchemy model.

        Returns:
            dict: A dictionary containing the model's column data (excluding internal attributes).
        """
        columns = model_instance.__table__.columns.keys()
        return {column: getattr(model_instance, column) for column in columns}

    async def add_single_on_conflict_do_nothing(self, model_instance: ModelInstance) -> None:
        """Add a single model instance to the database and ignore conflicts.

        If a conflict occurs (e.g., a unique constraint violation), the existing row is left unchanged.

        Args:
            model_instance (ModelInstance): The instance of the model to be added.
        """
        model_data = self._get_model_data(model_instance)
        await self.session.execute(pg_insert(model_instance.__class__).values(**model_data).on_conflict_do_nothing())

    async def add_single_on_conflict_do_update(self, model_instance: ModelInstance, conflict_column: str) -> None:
        """Add a single model instance to the database and update the row on conflict.

        If a conflict occurs (based on the specified conflict column), the existing row is updated with the new data.

        Args:
            model_instance (ModelInstance): The instance of the model to be added.
            conflict_column (str): The column to be checked for conflicts.
        """
        model_data = self._get_model_data(model_instance)

        insert_stmt = pg_insert(model_instance.__class__).values(**model_data)
        update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=[conflict_column],
            set_={k: insert_stmt.excluded[k] for k in model_data.keys()},  # noqa SIM118
        )
        await self.session.execute(update_stmt)

    async def add_many_on_conflict_do_nothing(self, model_instances: list[ModelInstance]) -> None:
        """Add multiple model instances to the database and ignore conflicts.

        If conflicts occur (e.g., unique constraint violations), the existing rows are left unchanged.

        Args:
            model_instances (list[ModelInstance]): A list of model instances to be added.
        """
        if model_instances:
            models_data = [self._get_model_data(model_instance=model_instance) for model_instance in model_instances]
            await self.session.execute(
                pg_insert(model_instances[0].__class__).values(models_data).on_conflict_do_nothing(),
            )

    async def add_many_on_conflict_do_update(self, model_instances: list[ModelInstance], conflict_column: str) -> None:
        """Add multiple model instances to the database and update rows on conflict.

        If conflicts occur (based on the specified conflict column), the existing rows are updated with the new data.

        Args:
            model_instances (list[ModelInstance]): A list of model instances to be added.
            conflict_column (str): The column to be checked for conflicts.
        """
        if model_instances:
            models_data = [self._get_model_data(model_instance=model_instance) for model_instance in model_instances]
            insert_stmt = pg_insert(models_data[0].__class__).values(models_data)
            update_stmt = insert_stmt.on_conflict_do_update(
                index_elements=[conflict_column],
                set_={k: insert_stmt.excluded[k] for k in models_data[0].keys()},  # noqa SIM118
            )
            await self.session.execute(update_stmt)

    async def get_single_row(self, model_class: type[ModelInstance], **filters: Any) -> ModelInstance | None:
        """Retrieve a single row from the database based on the provided filters.

        Args:
            model_class (type[ModelInstance]): The class of the model to query.
            **filters (Any): The filter criteria for selecting the row.

        Returns:
            ModelInstance | None: The retrieved model instance or None if no row matches the filters.
        """
        query = select(model_class).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_many_rows(self, model_class: type[ModelInstance], **filters: Any) -> list[ModelInstance | None]:
        """Retrieve multiple rows from the database based on the provided filters.

        Args:
            model_class (type[ModelInstance]): The class of the model to query.
            **filters (Any): The filter criteria for selecting the rows.

        Returns:
            list[ModelInstance | None]: A list of retrieved model instances, or None if no rows match the filters.
        """
        query = select(model_class).filter_by(**filters).order_by(model_class.created_at)  # type: ignore
        result = await self.session.execute(query)
        return list(result.scalars().fetchall())

    async def get_all_rows(self, model_class: type[ModelInstance]) -> list[ModelInstance | None]:
        """Retrieve all rows from the database for a given model class.

        Args:
            model_class (type[ModelInstance]): The class of the model to query.

        Returns:
            list[ModelInstance | None]: A list of all model instances in the table.
        """
        result = await self.session.execute(select(model_class))
        return list(result.scalars().fetchall())

    async def delete_single_row(self, model_class: type[ModelInstance], **filters: dict[str, Any]) -> None:
        """Delete a single row from the database based on the provided filters.

        Args:
            model_class (type[ModelInstance]): The class of the model to delete.
            **filters (dict[str, Any]): The filter criteria for selecting the row to delete.
        """
        await self.session.execute(delete(model_class).filter_by(**filters))

    async def delete_many_rows(self, model_class: type[ModelInstance], **filters: dict[str, Any]) -> None:
        """Delete multiple rows from the database based on the provided filters.

        Args:
            model_class (type[ModelInstance]): The class of the model to delete.
            **filters (dict[str, Any]): The filter criteria for selecting the rows to delete.
        """
        await self.session.execute(delete(model_class).filter_by(**filters))
