from fastapi.params import Depends

from portfolio_backend.services.chat.chat_handler import ChatHandler
from portfolio_backend.settings import settings
from portfolio_backend.vdb.dependencies import get_milvus_db
from portfolio_backend.vdb.milvus_connector import MilvusDB
from langchain_openai import ChatOpenAI


def get_chat_handler(milvus_db: MilvusDB = Depends(get_milvus_db)) -> ChatHandler:
    model = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key)
    return ChatHandler(llm_model=model, milvus_db=milvus_db)
