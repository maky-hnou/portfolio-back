"""Module providing a function to get a database session for async operations.

This module defines an asynchronous function `get_db_session` that creates and yields a database session
using the SQLAlchemy AsyncSession. The session is tied to the current request lifecycle.

Functions:
    get_db_session: Asynchronously creates and yields a database session for the current request.

Dependencies:
    - collections.abc.AsyncGenerator: Type hint for asynchronous generator.
    - sqlalchemy.ext.asyncio.AsyncSession: SQLAlchemy class for asynchronous database sessions.
    - starlette.requests.Request: Starlette class representing an HTTP request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session.

    Args:
        request (Request): The current request object.

    Yields:
        AsyncSession: An active database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:  # noqa: WPS501
        yield session
    finally:
        await session.commit()
        await session.close()
