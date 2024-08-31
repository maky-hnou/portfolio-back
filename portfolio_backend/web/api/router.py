from fastapi.routing import APIRouter

from portfolio_backend.web.api import chat, docs, echo, message, monitoring, text_data

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="", tags=["echo"])
api_router.include_router(chat.router, prefix="", tags=["chat"])
api_router.include_router(message.router, prefix="", tags=["message"])
api_router.include_router(text_data.router, prefix="", tags=["text_data"])
