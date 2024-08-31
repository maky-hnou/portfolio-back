from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.services.chat.config import prompt, general_context, ai_first_message
from portfolio_backend.web.api.chat.schema import ChatDTO
from portfolio_backend.web.api.message.schema import MessageDTO, MessageBy

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=ChatDTO)
async def get_chat(chat_id: str, chat_dao: ChatDAO = Depends()) -> ChatDTO:
    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDTO.model_validate(chat)


@router.post("/chat", response_model=ChatDTO)
async def create_chat(chat: ChatDTO, chat_dao: ChatDAO = Depends(), message_dao: MessageDAO = Depends()) -> ChatDTO:
    chat_model = ChatModel(**chat.dict())
    await chat_dao.add_single_on_conflict_do_nothing(model_instance=chat_model)
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
    await message_dao.add_many_on_conflict_do_nothing(model_instances=conversation)
    return ChatDTO.model_validate(chat_model)
