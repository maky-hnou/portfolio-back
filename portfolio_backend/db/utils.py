"""Module providing utility functions for database management.

This module includes functions for creating and dropping a PostgreSQL database using SQLAlchemy's
asynchronous engine. It checks for the existence of a database before creating a new one and
handles termination of active connections before dropping the database.

Functions:
    create_database: Asynchronously creates a PostgreSQL database if it does not already exist.
    drop_database: Asynchronously drops the specified PostgreSQL database.

Dependencies:
    - sqlalchemy: The SQLAlchemy ORM library for database interaction.
    - sqlalchemy.engine.make_url: Function to construct a database URL from a string.
    - sqlalchemy.ext.asyncio.create_async_engine: Function to create an asynchronous SQLAlchemy engine.
    - portfolio_backend.settings.settings: Configuration settings for the database connection.
"""

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from portfolio_backend.settings import settings


async def create_database() -> None:
    """Create a database.

    Returns:
        None
    """
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.db_base}'",  # noqa: E501, S608
            ),
        )
        database_exists = database_existance.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE DATABASE "{settings.db_base}" ENCODING "utf8" TEMPLATE template1',  # noqa: E501
            ),
        )


async def drop_database() -> None:
    """Drop current database.

    Returns:
        None
    """
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")
    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{settings.db_base}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{settings.db_base}"'))
