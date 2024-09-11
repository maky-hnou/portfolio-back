from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from loguru import logger

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
        logger.info("Initializing ChatHandler with LLM and MilvusDB")
        self.llm_model = llm_model
        self.milvus_db = milvus_db
        self.embedding_model = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,  # type: ignore
        )

    @staticmethod
    def _format_message(message: MessageDTO) -> BaseMessage:
        if message.message_by == MessageBy.HUMAN:
            return HumanMessage(content=message.message_text)
        if message.message_by == MessageBy.AI:
            return AIMessage(content=message.message_text)
        if message.message_by == MessageBy.SYSTEM:
            return SystemMessage(content=message.message_text)
        raise ValueError(f"Unexpected message_by value: {message.message_by}")

    def _update_conversation(
        self,
        old_conversation: list[MessageDTO],
        human_query: MessageDTO,
        system_message: str,
    ) -> list[BaseMessage]:
        logger.info(f"Updating conversation with new human query: {human_query.message_text}")
        old_conversation.append(human_query)
        # recreate the conversation by creating a list of responses (by system, ai, human)
        formatted_conversation = []
        for message in old_conversation:
            formatted_conversation.append(self._format_message(message=message))
        formatted_conversation.append(SystemMessage(system_message))
        logger.debug(f"Conversation updated with system message: {system_message}")
        return formatted_conversation

    async def handle_chat(
        self,
        conversation: list[MessageDTO],
        human_message: MessageDTO,
        off_topic_response_count: int,
    ) -> dict[str, str | None | int]:
        logger.info(
            f"Handling chat for message: {human_message.message_text} with off-topic count: {off_topic_response_count}",
        )

        # if len messages > 30, return limit length message
        if len(conversation) > messages_limit:
            logger.warning(f"Conversation length exceeded limit of {messages_limit}.")
            ai_message = limit_length_message
            system_message = None
        # if off-topic count < 3, embed the last message and use it to query the vector database
        elif off_topic_response_count < off_topic_count_limit:
            logger.info(f"Embedding message for vector search: {human_message.message_text}")
            query_embedding = Embedding(text=human_message.message_text, embedding_model=self.embedding_model)
            query_result = self.milvus_db.search(
                collection_name=vdb_config.collection_name,
                search_data=[query_embedding.text_embedding],
                limit=vdb_config.topk,
                output_fields=["text"],
                search_params=vdb_config.search_params,
                threshold=vdb_config.threshold,
            )
            logger.info(f"Query result from MilvusDB: {query_result}")
            system_message = prompt.format(context=query_result)
            formatted_conversation = self._update_conversation(
                old_conversation=conversation,
                human_query=human_message,
                system_message=system_message,
            )
            # send the conversation to openai api and get the response
            logger.info("Sending conversation to LLM for response.")
            response = self.llm_model.invoke(input=formatted_conversation)
            ai_message = response.content  # type: ignore
            logger.info(f"Received AI message: {ai_message}")

            # if the response is None, increment off-topic count and send off-topic message as response
            if "null" in ai_message.lower():
                logger.warning("AI response was off-topic.")
                off_topic_response_count += 1
                ai_message = off_topic_response.format(off_topic_count=off_topic_response_count)
        # else (if off-topic count exceeds 3), send the off-topic message
        else:
            logger.warning("Off-topic count exceeded the limit.")
            ai_message = limit_out_of_topic_message
            system_message = None

        # return the message + off-topic count
        logger.info(
            f"Returning system message: {system_message}, AI message: {ai_message}, off-topic count: {off_topic_response_count}"
        )
        return {
            "system_message": system_message,
            "ai_message": ai_message,
            "off_topic_response_count": off_topic_response_count,
        }
