from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.web.api.chat.schema import ChatDTO

router = APIRouter()


@router.get("/chat/{chat_id}", response_model=ChatDTO)
async def get_chat(chat_id: str, chat_dao: ChatDAO = Depends()) -> ChatDTO:
    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatDTO.model_validate(chat)


@router.post("/chat/", response_model=ChatDTO)
async def create_chat(chat: ChatDTO, chat_dao: ChatDAO = Depends()) -> ChatDTO:
    chat_model = ChatModel(**chat.dict())
    await chat_dao.add_single_on_conflict_do_nothing(model_instance=chat_model)
    return ChatDTO.model_validate(chat_model)
