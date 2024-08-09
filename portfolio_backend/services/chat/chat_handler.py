# todo
# receive the message from the endpoint (MessageDTO)
# use the chat_id from the message to retrieve all the messages of the chat from the DB
#
import re
from uuid import uuid4

from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from portfolio_backend.db.dao.chat_dao import ChatDAO
from portfolio_backend.db.dao.message_dao import MessageDAO
from portfolio_backend.db.models.chat_model import ChatModel
from portfolio_backend.db.models.message_model import MessageModel
from portfolio_backend.services.embeddor.embeddings import Embedding
from portfolio_backend.settings import settings
from portfolio_backend.vdb.configs import vdb_config
from portfolio_backend.vdb.milvus_connector import MilvusDB
from portfolio_backend.web.api.message.schema import MessageDTO, MessageBy
from portfolio_backend.services.chat.config import prompt, off_topic_response, limit_length_message, limit_out_of_topic_message


class ChatHandler:
    def __init__(self, llm_model: ChatOpenAI):
        self.llm_model = llm_model
        self.embedding_model = OpenAIEmbeddings(model=settings.embedding_model, openai_api_key=settings.openai_api_key)
        self.config = {"configurable": {"session_id": str(uuid4())}}
        self.store = {}
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        self.chain = self.prompt | self.llm_model
        self.chat_history = RunnableWithMessageHistory(
            self.chain,
            get_session_history=self._get_session_history,
            input_messages_key="messages",
        )
        print("*" * 100)
        print(self.store)
        print(self.config)
        print(self.store)
        print("*" * 100)

    def _get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self.store:
            self.store[session_id] = InMemoryChatMessageHistory()
        return self.store[session_id]

    async def handle_chat(self, message: MessageDTO, off_topic_response_count: int) -> dict[str, str | int]:
        # if len(self.store.get(self.config.get("configurable", {}).get("session_id"))) > 30:
        #     return {"ai_response": limit_length_message, "off_topic_response_count": off_topic_response_count}
        if off_topic_response_count < 3:
            print(f"message_text: {message.message_text}")
            query_embedding = Embedding(text=message.message_text, embedding_model=self.embedding_model)
            milvus_db = MilvusDB(db=vdb_config.vdb_name)
            query_result = milvus_db.search(
                collection_name=vdb_config.collection_name,
                search_data=[query_embedding.text_embedding],
                limit=vdb_config.topk,
                output_fields=["text"],
                search_params=vdb_config.search_params,
                threshold=vdb_config.threshold,

            )
            print(f"query_result: {query_result}")
            response = self.chat_history.invoke(
                {"messages": [HumanMessage(content="What's the text talking about?")], "context": query_result},
                config=self.config,
            )
            final_response = response.content

            if response.content is None:
                off_topic_response_count += 1
                final_response = off_topic_response.format(off_topic_count=off_topic_response_count)
        else:
            final_response = limit_out_of_topic_message

        print(f"config: {self.config}")
        print(f"store: {self.store}")
        print(f"final_response: {final_response}")
        return {"ai_response": final_response, "off_topic_response_count": off_topic_response_count}
