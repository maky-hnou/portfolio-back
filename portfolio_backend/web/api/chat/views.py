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
