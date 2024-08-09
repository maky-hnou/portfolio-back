from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends
from langchain_openai import ChatOpenAI

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.services.chat.chat_handler import ChatHandler
from portfolio_backend.settings import settings
from portfolio_backend.web.api.message.schema import MessageBy, MessageDTO

router = APIRouter()
model = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key)
chat_handler = ChatHandler(llm_model=model)


@router.get("/message/{message_id}", response_model=MessageDTO)
async def get_message(message_id: str, message_dao: MessageDAO = Depends()) -> MessageModel | None:
    message = await message_dao.get_single_row(model_class=MessageModel, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.get("/message/chat/{chat_id}", response_model=list[MessageDTO])
async def get_all_chat_messages(chat_id: str, message_dao: MessageDAO = Depends()) -> list[MessageDTO | None]:
    messages = await message_dao.get_many_rows(model_class=MessageModel, chat_id=chat_id)
    return [MessageDTO.model_validate(message) for message in messages]


@router.post("/message", response_model=MessageDTO)
async def create_message(
    message: MessageDTO, message_dao: MessageDAO = Depends(), chat_dao: ChatDAO = Depends()
) -> MessageDTO:
    print(f"Message: {message}")
    message_model = MessageModel(**message.dict())
    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=message.chat_id)
    await message_dao.add_single_on_conflict_do_nothing(model_instance=message_model)
    ai_response = await chat_handler.handle_chat(
        message=message, off_topic_response_count=chat.off_topic_response_count
    )
    if ai_response.get("off_topic_response_count") != chat.off_topic_response_count:
        chat.off_topic_response_count = ai_response.get("off_topic_response_count")
        await chat_dao.add_single_on_conflict_do_update(model_instance=chat, conflict_column="chat_id")
    ai_message = MessageDTO(chat_id=chat.chat_id, message_text=ai_response.get("ai_response"), message_by=MessageBy.AI)
    return ai_message
