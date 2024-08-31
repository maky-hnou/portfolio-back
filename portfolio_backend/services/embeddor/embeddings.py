import tiktoken
from langchain_openai import OpenAIEmbeddings

from portfolio_backend.settings import settings


class Embedding:
    def __init__(self, text: str, embedding_model: OpenAIEmbeddings | None = None):
        self.text = text.replace("\n", " ")
        if not embedding_model:
            embedding_model = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,  # type: ignore
            )
        self.embedding_model = embedding_model

    @property
    def tokens_count(self) -> int:
        encoding = tiktoken.get_encoding(settings.encoding_name)
        return len(encoding.encode(self.text))

    @property
    def estimated_cost(self) -> float:
        return self.tokens_count * settings.token_cost

    @property
    def text_embedding(self) -> list[float]:
        return self.embedding_model.embed_query(text=self.text)
