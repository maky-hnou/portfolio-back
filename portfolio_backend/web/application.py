"""Module for configuring and creating the FastAPI application instance.

This module sets up the main FastAPI application for the portfolio backend,
including middleware configuration, static file serving, CORS setup,
and the inclusion of API routes. The application is constructed using
FastAPI's `FastAPI` class, with logging configured and startup/shutdown
events registered.

Dependencies:
    - FastAPI: The main class for building the web application.
    - UJSONResponse: FastAPI response class for JSON responses using ujson.
    - StaticFiles: Middleware for serving static files.
    - CORSMiddleware: Middleware for handling Cross-Origin Resource Sharing.
    - metadata: Module for accessing package metadata.
    - Path: Class for manipulating filesystem paths.
    - configure_logging: Function to set up logging configuration.
    - api_router: The main API router for the application.
    - register_shutdown_event: Function to register shutdown event handlers.
    - register_startup_event: Function to register startup event handlers.
"""

from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from portfolio_backend.logging import configure_logging
from portfolio_backend.web.api.router import api_router
from portfolio_backend.web.lifetime import (
    register_shutdown_event,
    register_startup_event,
)

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """Create and configure a FastAPI application instance.

    Returns:
        FastAPI: The configured FastAPI application instance.
    """
    configure_logging()
    app = FastAPI(
        title="portfolio_backend",
        version=metadata.version("portfolio_backend"),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Adds startup and shutdown events.
    register_startup_event(app)
    register_shutdown_event(app)

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api/v1")
    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount(
        "/static",
        StaticFiles(directory=APP_ROOT / "static"),
        name="static",
    )

    # Set CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        # allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
