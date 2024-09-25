"""
This module handles Alembic database migrations for the application.

It defines functions to run migrations in both 'offline' and 'online' modes, 
using SQLAlchemy's async engine for database connections.

The `run_migrations_offline` function handles offline migrations, configuring the 
migration context with a URL, while `run_migrations_online` sets up an asynchronous 
connection to the database and runs the migrations in online mode. The `do_run_migrations` 
helper function is used to configure the context and execute migrations synchronously 
within the given connection.

Logging is configured using the settings from Alembic's config file, and the metadata 
from all models is loaded to support autogeneration of migrations.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.future import Connection

from portfolio_backend.db.meta import meta
from portfolio_backend.db.models import load_all_models
from portfolio_backend.settings import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


load_all_models()
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = meta

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


async def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Returns:
        None
    """
    context.configure(
        url=str(settings.db_url),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    Run synchronous migrations with the provided connection.

    Args:
        connection (Connection): A SQLAlchemy connection object used to perform
        the migrations.

    Returns:
        None
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    Returns:
        None
    """
    connectable = create_async_engine(str(settings.db_url))

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


loop = asyncio.get_event_loop()
if context.is_offline_mode():
    task = run_migrations_offline()
else:
    task = run_migrations_online()

loop.run_until_complete(task)
