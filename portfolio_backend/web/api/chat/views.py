"""Module defining chat-related API endpoints for handling chat creation and retrieval.

This module contains API routes for creating new chat instances and fetching existing ones.
It utilizes data access objects (DAOs) for interacting with the database, and schema models
for data transfer. Additionally, it enforces rate limiting on chat creation.

Routes:
    get_chat: Retrieve a specific chat by its ID.
    create_chat: Create a new chat and initialize the conversation with system and AI messages.

Dependencies:
    - APIRouter: FastAPI router class for creating API endpoints.
    - ChatDAO: DAO class for managing chat-related database interactions.
    - MessageDAO: DAO class for managing message-related database interactions.
    - ChatModel: Pydantic model representing the chat in the database.
    - MessageModel: Pydantic model representing messages in the database.
    - ChatDTO: Data transfer object for chat data.
    - MessageDTO: Data transfer object for message data.
    - MessageBy: Enum defining the origin of a message (e.g., SYSTEM, AI).
    - limiter: Custom rate limiter for controlling API request frequency.
    - loguru: Logging utility for tracking API interactions.
"""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.param_functions import Depends
from loguru import logger

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.services.chat.config import ai_first_message, general_context, prompt
from portfolio_backend.web.api.chat.schema import ChatDTO
from portfolio_backend.web.api.message.schema import MessageBy, MessageDTO
from portfolio_backend.web.rate_limiter import limiter

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=ChatDTO)
async def get_chat(chat_id: str, chat_dao: ChatDAO = Depends()) -> ChatDTO:
    """Retrieve a specific chat by its unique identifier.

    Args:
        chat_id (str): The unique identifier for the chat.
        chat_dao (ChatDAO): The data access object responsible for fetching the chat data.
            Defaults to being injected via FastAPI's `Depends`.

    Returns:
        ChatDTO: The chat data transfer object representing the chat details.

    Raises:
        HTTPException: If the chat is not found in the database, a 404 error is raised.
    """
    logger.info(f"Fetching chat with id: {chat_id}")
    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=chat_id)
    if chat is None:
        logger.warning(f"Chat with id {chat_id} not found.")
        raise HTTPException(status_code=404, detail="Chat not found")
    logger.info(f"Chat with id {chat_id} found: {chat}")
    return ChatDTO.model_validate(chat)


@router.post("/chat", response_model=ChatDTO)
@limiter.limit("2 per 5 minute", error_message="Rate limit 2 per 5 minutes exceeded for creating a chat.")
async def create_chat(
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
    chat: ChatDTO,
    chat_dao: ChatDAO = Depends(),
    message_dao: MessageDAO = Depends(),
) -> ChatDTO:
    """Create a new chat and add system and AI messages to the conversation.

    Args:
        request (Request): The HTTP request object (unused but required for middleware).
        response (Response): The HTTP response object (unused but required for middleware).
        chat (ChatDTO): The chat data transfer object containing chat creation details.
        chat_dao (ChatDAO): The data access object for handling chat-related database operations.
        message_dao (MessageDAO): The data access object for handling message-related database operations.

    Returns:
        ChatDTO: The created chat object with its unique identifier and associated data.
    """
    logger.info(f"Creating new chat with data: {chat.dict()}")
    chat_model = ChatModel(**chat.dict())
    await chat_dao.add_single_on_conflict_do_nothing(model_instance=chat_model)
    logger.info(f"Chat created with id: {chat.chat_id}")

    system_message = MessageDTO(
        chat_id=chat.chat_id,
        message_text=prompt.format(context=general_context),
        message_by=MessageBy.SYSTEM,
    )
    ai_message = MessageDTO(
        chat_id=chat.chat_id,
        message_text=ai_first_message,
        message_by=MessageBy.AI,
    )
    conversation = [MessageModel(**system_message.dict()), MessageModel(**ai_message.dict())]
    logger.info(f"Adding system and AI messages to chat with id: {chat.chat_id}")
    await message_dao.add_many_on_conflict_do_nothing(model_instances=conversation)

    logger.info(f"Chat creation process completed for id: {chat.chat_id}")
    return ChatDTO.model_validate(chat_model)
