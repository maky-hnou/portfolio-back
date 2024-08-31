# todo
# receive the message from the endpoint (MessageDTO)
# use the chat_id from the message to retrieve all the messages of the chat from the DB
#

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from portfolio_backend.services.chat.config import (
    limit_length_message,
    limit_out_of_topic_message,
    messages_limit,
    off_topic_count_limit,
    off_topic_response,
    prompt,
)
from portfolio_backend.services.embeddor.embeddings import Embedding
from portfolio_backend.settings import settings
from portfolio_backend.vdb.configs import vdb_config
from portfolio_backend.vdb.milvus_connector import MilvusDB
from portfolio_backend.web.api.message.schema import MessageBy, MessageDTO


class ChatHandler:
    def __init__(self, llm_model: ChatOpenAI, milvus_db: MilvusDB):
        print("Init ChatHandler")
        self.llm_model = llm_model
        self.milvus_db = milvus_db
        self.embedding_model = OpenAIEmbeddings(model=settings.embedding_model, openai_api_key=settings.openai_api_key)

    @staticmethod
    def _format_message(message: MessageDTO) -> BaseMessage:
        if message.message_by == MessageBy.HUMAN:
            return HumanMessage(content=message.message_text)
        if message.message_by == MessageBy.AI:
            return AIMessage(content=message.message_text)
        if message.message_by == MessageBy.SYSTEM:
            return SystemMessage(content=message.message_text)
        raise ValueError(f"Unexpected message_by value: {message.message_by}")

    async def handle_chat(
            self,
            conversation: list[MessageDTO],
            human_message: MessageDTO,
            off_topic_response_count: int
    ) -> dict[str, str | None | MessageDTO | int]:
        # if len messages > 30, return limit length message
        if len(conversation) > messages_limit:
            ai_message = limit_length_message
            system_message = None
        # if off-topic count < 3, embed the last message and use it to query the vector database
        elif off_topic_response_count < off_topic_count_limit:
            query_embedding = Embedding(text=human_message.message_text, embedding_model=self.embedding_model)
            query_result = self.milvus_db.search(
                collection_name=vdb_config.collection_name,
                search_data=[query_embedding.text_embedding],
                limit=vdb_config.topk,
                output_fields=["text"],
                search_params=vdb_config.search_params,
                threshold=vdb_config.threshold,

            )
            system_message = MessageDTO(
                chat_id=human_message.chat_id,
                message_text=prompt.format(context=query_result),
                message_by=MessageBy.SYSTEM,
            )
            conversation.append(human_message)
            conversation.append(system_message)
            # recreate the conversation by creating a list of responses (by system, ai, human)
            formatted_conversation = []
            for message in conversation:
                formatted_conversation.append(self._format_message(message=message))
            # send the conversation to openai api and get the response
            response = self.llm_model.invoke(input=formatted_conversation)
            ai_message = response.content
            # if the response is None, increment off-topic count and send off-topic message as response
            if "none" in ai_message.lower():
                off_topic_response_count += 1
                ai_message = off_topic_response.format(off_topic_count=off_topic_response_count)
        # else (of line 58) off-topic count exceeds 3, send the off-topic message and the off-topic count
        else:
            ai_message = limit_out_of_topic_message
            system_message = None
        # return the message + off-topic count
        return {
            "system_message": system_message,
            "ai_message": ai_message,
            "off_topic_response_count": off_topic_response_count,
        }
