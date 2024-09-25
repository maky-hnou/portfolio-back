"""Module containing the MessageDAO class for managing database operations related to the Message model.

This module extends the BaseDAO class to handle CRUD operations specific to the Message model within an
asynchronous FastAPI environment. It allows querying messages based on filters and includes additional
filtering by `message_by` field.

Classes:
    MessageDAO: A Data Access Object (DAO) class that provides methods for managing Message model records.

Dependencies:
    - BaseDAO: Inherited class that provides basic CRUD operations.
    - AsyncSession: SQLAlchemy asynchronous session, injected via FastAPI's dependency system.
    - MessageModel: The SQLAlchemy model class for messages, representing the structure of the message table.
"""

from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.dao.base_dao import BaseDAO
from portfolio_backend.db.dependencies import get_db_session
from portfolio_backend.db.models.message_model import MessageModel


class MessageDAO(BaseDAO):
    """DAO class for Message.

    Args:
        session (AsyncSession): The asynchronous database session used for Message model transactions.
    """

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        """Initialize the MessageDAO with a database session.

        Calls the BaseDAO constructor to initialize the session attribute.

        Args:
            session (AsyncSession): The database session used for Message model transactions.
        """
        super().__init__(session)

    async def get_many_rows(  # type: ignore
        self,
        model_class: type[MessageModel],
        message_by: list[str] | None = None,
        **filters: Any,
    ) -> list[MessageModel | None]:
        """Retrieve multiple Message model rows based on filters and an optional message_by filter.

        Args:
            model_class (type[MessageModel]): The class of the Message model to query.
            message_by (list[str] | None): An optional list of `message_by` values to filter the messages.
            **filters (Any): Additional filter criteria for selecting rows.

        Returns:
            list[MessageModel | None]: A list of Message model instances that match the filters.
        """
        query = select(model_class).filter_by(**filters)

        # Apply the additional filter if message_by is provided
        if message_by:
            query = query.filter(model_class.message_by.in_(message_by))

        query = query.order_by(model_class.created_at)

        result = await self.session.execute(query)
        return list(result.scalars().fetchall())
