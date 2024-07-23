import tiktoken
from openai import OpenAI

from portfolio_backend.settings import settings


class Embedding:
    def __init__(self, text: str, openai_client: OpenAI):
        self.text = text.replace("\n", " ")
        self.openai_client = openai_client

    @property
    def tokens(self) -> int:
        encoding = tiktoken.get_encoding(settings.encoding_name)
        return len(encoding.encode(self.text))

    @property
    def estimated_cost(self) -> float:
        return self.tokens * settings.token_cost

    @property
    def text_embedding(self) -> list[float]:
        return self.openai_client.embeddings.create(input=[self.text], model=settings.embedding_model).data[0].embedding
