"""Module defining message-related API endpoints for managing chat messages.

This module provides API routes for creating, retrieving, and processing messages in chats.
It integrates with a custom ChatHandler service to handle conversation flow and process AI
responses to human messages. The module also includes rate-limiting for message creation.

Routes:
    get_message: Retrieve a single message by its ID.
    get_all_chat_messages: Retrieve all messages for a specific chat.
    create_message: Create a new message from a human and generate AI/system responses.

Dependencies:
    - APIRouter: FastAPI router class for creating API endpoints.
    - ChatDAO: DAO class for managing chat-related database interactions.
    - MessageDAO: DAO class for managing message-related database interactions.
    - ChatModel: Pydantic model representing the chat in the database.
    - MessageModel: Pydantic model representing messages in the database.
    - MessageDTO: Data transfer object for message data.
    - MessageBy: Enum defining the origin of a message (e.g., HUMAN, AI, SYSTEM).
    - ChatHandler: Service class responsible for handling chat conversation logic.
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
from portfolio_backend.services.chat.chat_handler import ChatHandler
from portfolio_backend.services.chat.dependencies import get_chat_handler
from portfolio_backend.web.api.message.schema import MessageBy, MessageDTO
from portfolio_backend.web.rate_limiter import limiter

router = APIRouter()


@router.get("/message/{message_id}", response_model=MessageDTO)
async def get_message(message_id: str, message_dao: MessageDAO = Depends()) -> MessageModel | None:
    """Retrieve a single message by its unique identifier.

    Args:
        message_id (str): The unique identifier for the message.
        message_dao (MessageDAO): The data access object responsible for fetching message data.
            Defaults to being injected via FastAPI's `Depends`.

    Returns:
        MessageModel | None: The message object if found, otherwise raises a 404 error.

    Raises:
        HTTPException: If the message is not found in the database, a 404 error is raised.
    """
    logger.info(f"Fetching message with id: {message_id}")
    message = await message_dao.get_single_row(model_class=MessageModel, message_id=message_id)
    if message is None:
        logger.warning(f"Message with id {message_id} not found.")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info(f"Message with id {message_id} found: {message}")
    return message


@router.get("/message/chat/{chat_id}", response_model=list[MessageDTO])
async def get_all_chat_messages(chat_id: str, message_dao: MessageDAO = Depends()) -> list[MessageDTO | None]:
    """Retrieve all messages for a specific chat.

    Args:
        chat_id (str): The unique identifier for the chat.
        message_dao (MessageDAO): The data access object responsible for fetching message data.
            Defaults to being injected via FastAPI's `Depends`.

    Returns:
        list[MessageDTO | None]: A list of message data transfer objects for the chat.
    """
    logger.info(f"Fetching all messages for chat with id: {chat_id}")
    messages = await message_dao.get_many_rows(model_class=MessageModel, chat_id=chat_id)
    logger.info(f"Found {len(messages)} messages for chat with id: {chat_id}")
    return [MessageDTO.model_validate(message) for message in messages]


@router.post("/message", response_model=MessageDTO)
@limiter.limit("50 per 5 minute", error_message="Rate limit 50 per 5 minutes exceeded for creating messages.")
async def create_message(  # noqa: PLR0913
    request: Request,  # noqa: ARG001
    response: Response,  # noqa: ARG001
    human_message: MessageDTO,
    message_dao: MessageDAO = Depends(),
    chat_dao: ChatDAO = Depends(),
    chat_handler: ChatHandler = Depends(get_chat_handler),
) -> MessageDTO:
    """Create a new human message and generate system/AI responses.

    Args:
        request (Request): The HTTP request object (unused but required for middleware).
        response (Response): The HTTP response object (unused but required for middleware).
        human_message (MessageDTO): The message data transfer object containing the human message details.
        message_dao (MessageDAO): DAO for handling message-related database operations.
        chat_dao (ChatDAO): DAO for handling chat-related database operations.
        chat_handler (ChatHandler): Service for managing chat logic, responsible for AI/system message generation.

    Returns:
        MessageDTO: The message data transfer object representing the AI response message.
    """
    logger.info(f"Creating new message for chat id: {human_message.chat_id}")

    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=human_message.chat_id)
    logger.info(f"Chat fetched for message creation: {chat}")

    conversation = await message_dao.get_many_rows(
        model_class=MessageModel,
        chat_id=human_message.chat_id,
        message_by=[MessageBy.HUMAN, MessageBy.AI],
    )
    logger.info(f"Conversation history for chat id {human_message.chat_id} fetched with {len(conversation)} messages.")

    conversation_dto = [MessageDTO.model_validate(message) for message in conversation]
    ai_response = await chat_handler.handle_chat(
        conversation=conversation_dto,
        human_message=human_message,
        off_topic_response_count=chat.off_topic_response_count,  # type: ignore
    )
    logger.info(f"AI response received for chat id {human_message.chat_id}: {ai_response}")

    messages = [MessageModel(**human_message.dict())]
    if ai_response.system_message:
        system_message = MessageDTO(
            chat_id=chat.chat_id,  # type: ignore
            message_text=ai_response.system_message,
            message_by=MessageBy.SYSTEM,
        )
        messages.append(MessageModel(**system_message.dict()))
        logger.info(f"System message added to conversation for chat id {chat.chat_id}")  # type: ignore

    ai_message = MessageDTO(
        chat_id=chat.chat_id,  # type: ignore
        message_text=ai_response.ai_message,
        message_by=MessageBy.AI,
    )
    messages.append(MessageModel(**ai_message.dict()))
    logger.info(f"AI message added to conversation for chat id {chat.chat_id}")  # type: ignore

    await message_dao.add_many_on_conflict_do_nothing(model_instances=messages)
    logger.info(f"Messages saved for chat id {chat.chat_id}")  # type: ignore

    if ai_response.off_topic_response_count != chat.off_topic_response_count:  # type: ignore
        chat.off_topic_response_count = ai_response.off_topic_response_count  # type: ignore
        await chat_dao.add_single_on_conflict_do_update(
            model_instance=chat,
            conflict_column="chat_id",
        )  # type: ignore
        logger.info(
            f"Updated off-topic response count for chat id {chat.chat_id}: {chat.off_topic_response_count}",  # type: ignore
        )

    return MessageDTO(
        chat_id=chat.chat_id,  # type: ignore
        message_text=ai_response.ai_message,
        message_by=MessageBy.AI,
    )
