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
    logger.info(f"Fetching message with id: {message_id}")
    message = await message_dao.get_single_row(model_class=MessageModel, message_id=message_id)
    if message is None:
        logger.warning(f"Message with id {message_id} not found.")
        raise HTTPException(status_code=404, detail="Message not found")
    logger.info(f"Message with id {message_id} found: {message}")
    return message


@router.get("/message/chat/{chat_id}", response_model=list[MessageDTO])
async def get_all_chat_messages(chat_id: str, message_dao: MessageDAO = Depends()) -> list[MessageDTO | None]:
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
