from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Depends

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.services.chat.chat_handler import ChatHandler
from portfolio_backend.services.chat.dependencies import get_chat_handler
from portfolio_backend.web.api.message.schema import MessageBy, MessageDTO

router = APIRouter()


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
    human_message: MessageDTO,
    message_dao: MessageDAO = Depends(),
    chat_dao: ChatDAO = Depends(),
    chat_handler: ChatHandler = Depends(get_chat_handler),
) -> MessageDTO:
    chat = await chat_dao.get_single_row(model_class=ChatModel, chat_id=human_message.chat_id)
    conversation = await message_dao.get_many_rows(
        model_class=MessageModel,
        chat_id=human_message.chat_id,
        message_by=[MessageBy.HUMAN, MessageBy.AI],
    )
    conversation_dto = [MessageDTO.model_validate(message) for message in conversation]
    ai_response = await chat_handler.handle_chat(
        conversation=conversation_dto,
        human_message=human_message,
        off_topic_response_count=chat.off_topic_response_count,  # type: ignore
    )
    messages = [MessageModel(**human_message.dict())]
    if ai_response.get("system_message"):
        system_message = MessageDTO(
            chat_id=chat.chat_id,  # type: ignore
            message_text=ai_response.get("system_message"),  # type: ignore
            message_by=MessageBy.SYSTEM,
        )
        messages.append(MessageModel(**system_message.dict()))
    ai_message = MessageDTO(
        chat_id=chat.chat_id,  # type: ignore
        message_text=ai_response.get("ai_message"),  # type: ignore
        message_by=MessageBy.AI,
    )
    messages.append(MessageModel(**ai_message.dict()))
    await message_dao.add_many_on_conflict_do_nothing(model_instances=messages)
    if ai_response.get("off_topic_response_count") != chat.off_topic_response_count:  # type: ignore
        chat.off_topic_response_count = ai_response.get("off_topic_response_count")  # type: ignore
        await chat_dao.add_single_on_conflict_do_update(
            model_instance=chat,
            conflict_column="chat_id",
        )  # type: ignore
    return MessageDTO(
        chat_id=chat.chat_id,  # type: ignore
        message_text=ai_response.get("ai_message"),  # type: ignore
        message_by=MessageBy.AI,
    )
