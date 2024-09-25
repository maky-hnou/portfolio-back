"""Module containing the ChatDAO class for managing database operations related to the Chat model.

This module extends the BaseDAO class to handle CRUD operations specific to the Chat model within an
asynchronous FastAPI environment. It uses SQLAlchemy's AsyncSession and FastAPI's dependency injection
for database session management.

Classes:
    ChatDAO: A Data Access Object (DAO) class that provides methods for managing Chat model records.

Dependencies:
    - BaseDAO: Inherited class that provides basic CRUD operations.
    - AsyncSession: SQLAlchemy asynchronous session, injected via FastAPI's dependency system.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from portfolio_backend.db.dao.base_dao import BaseDAO
from portfolio_backend.db.dependencies import get_db_session


class ChatDAO(BaseDAO):
    """DAO class for Chat.

    Args:
        session (AsyncSession): The asynchronous database session used for Message model transactions.
    """

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        """Initialize the ChatDAO with a database session.

        Calls the BaseDAO constructor to initialize the session attribute.

        Args:
            session (AsyncSession): The database session used for Chat model transactions.
        """
        super().__init__(session)
