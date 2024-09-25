"""Module for providing dependencies related to the chat handler.

This module contains functions to create and manage instances of the `ChatHandler`, which interacts with
the language model and the Milvus vector database for chat functionalities.

Dependencies:
    - FastAPI: For dependency injection.
    - Langchain OpenAI: For accessing the OpenAI chat model.
    - Portfolio backend services: For accessing chat handler and Milvus database functionalities.

Functions:
    get_chat_handler(milvus_db: MilvusDB = Depends(get_milvus_db)) -> ChatHandler:
        Create and return an instance of the ChatHandler.
"""

from fastapi.params import Depends
from langchain_openai import ChatOpenAI

from portfolio_backend.services.chat.chat_handler import ChatHandler
from portfolio_backend.settings import settings
from portfolio_backend.vdb.dependencies import get_milvus_db
from portfolio_backend.vdb.milvus_connector import MilvusDB


def get_chat_handler(milvus_db: MilvusDB = Depends(get_milvus_db)) -> ChatHandler:  # type: ignore
    """Create an instance of the ChatHandler with the required dependencies.

    Args:
        milvus_db (MilvusDB, optional): An instance of the Milvus database for embedding queries.
            Defaults to the result of `get_milvus_db`.

    Returns:
        ChatHandler: An instance of the ChatHandler configured with the OpenAI chat model and MilvusDB.
    """
    model = ChatOpenAI(model=settings.chat_model, api_key=settings.openai_api_key)  # type: ignore
    return ChatHandler(llm_model=model, milvus_db=milvus_db)
