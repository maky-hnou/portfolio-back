from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.web.api.message.schema import MessageDTO

router = APIRouter()


@router.get("/message/{message_id}", response_model=MessageDTO)
async def get_message(message_id: str, message_dao: MessageDAO = Depends()) -> MessageModel | None:
    message = await message_dao.get_single_row(model_class=MessageModel, message_id=message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.get("/message/chat/{chat_id}", response_model=list[MessageDTO])
async def get_all_chat_messages(chat_id: str, message_dao: MessageDAO = Depends()) -> list[MessageModel | None]:
    return await message_dao.get_many_rows(model_class=MessageModel, chat_id=chat_id)


@router.post("/message/", response_model=MessageDTO)
async def create_message(message: MessageDTO, chat_dao: MessageDAO = Depends()) -> MessageModel:
    message_model = MessageModel(**message.dict())
    await chat_dao.add_single_on_conflict_do_nothing(model_instance=message_model)
    return message_model
