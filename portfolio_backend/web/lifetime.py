"""Module for managing FastAPI application startup and shutdown events.

This module provides functions for setting up the database connection,
enabling Prometheus integration for monitoring, and registering
startup and shutdown events for the FastAPI application. It manages
the application's state, storing instances of the database engine,
session factory, Milvus database connector, Redis client, and rate limiter.

Dependencies:
    - FastAPI: The main class for building the web application.
    - PrometheusFastApiInstrumentator: Class for integrating Prometheus monitoring.
    - Redis: Class for connecting to a Redis database.
    - async_sessionmaker: Factory for creating asynchronous database sessions.
    - create_async_engine: Function for creating an asynchronous SQLAlchemy engine.
    - settings: Module containing application configuration settings.
    - vdb_config: Configuration for the vector database.
    - MilvusDB: Class for connecting to the Milvus vector database.
    - limiter: Rate limiter for API requests.
"""

from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from prometheus_fastapi_instrumentator.instrumentation import (
    PrometheusFastApiInstrumentator,
)
from redis import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from portfolio_backend.settings import settings
from portfolio_backend.vdb.configs import vdb_config
from portfolio_backend.vdb.milvus_connector import MilvusDB
from portfolio_backend.web.rate_limiter import limiter


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """Create connection to the database.

    This function creates an SQLAlchemy engine instance,
    a session factory for creating sessions, and stores them
    in the application's state property.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    # Initialize Milvus DB
    app.state.milvus_db = MilvusDB(db=vdb_config.vdb_name)
    app.state.redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)
    app.state.limiter = limiter


def setup_prometheus(app: FastAPI) -> None:  # pragma: no cover
    """Enable Prometheus integration.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    PrometheusFastApiInstrumentator(should_group_status_codes=False).instrument(
        app,
    ).expose(app, should_gzip=True, name="prometheus_metrics")


def register_startup_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """Register actions to run on application startup.

    This function uses the FastAPI app to store data
    in the state, such as db_engine.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        Callable[[], Awaitable[None]]: A function that performs startup actions.
    """

    @app.on_event("startup")
    async def _startup() -> None:  # noqa: WPS430
        app.middleware_stack = None
        _setup_db(app)
        setup_prometheus(app)
        app.middleware_stack = app.build_middleware_stack()
        pass  # noqa: WPS420

    return _startup


def register_shutdown_event(app: FastAPI) -> Callable[[], Awaitable[None]]:  # pragma: no cover
    """Register actions to run on application shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Returns:
        Callable[[], Awaitable[None]]: A function that performs shutdown actions.
    """

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()
        app.state.milvus_db.close_connection()

        pass  # noqa: WPS420

    return _shutdown
