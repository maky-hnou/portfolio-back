"""Module for setting up and organizing API routes.

This module defines an `APIRouter` instance that includes multiple route modules
for different functionalities, such as chat, message, text data management, documentation,
and monitoring endpoints. Each route module is associated with a specific functionality
and is integrated into the main API router.

Routers:
    - chat: Handles chat-related operations.
    - docs: Provides API documentation.
    - message: Handles message-related operations.
    - monitoring: Health and performance monitoring routes.
    - text_data: Handles operations related to text data management.

Dependencies:
    - APIRouter: FastAPI class for grouping routes and including sub-routers.
"""

from fastapi.routing import APIRouter

from portfolio_backend.web.api import chat, docs, message, monitoring, text_data

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(chat.router, prefix="", tags=["chat"])
api_router.include_router(message.router, prefix="", tags=["message"])
api_router.include_router(text_data.router, prefix="", tags=["text_data"])
