"""Module for managing text embeddings using the OpenAI model.

This module provides the `Embedding` class, which handles the creation of text embeddings and
calculates associated properties such as token count and estimated cost.

Dependencies:
    - Tiktoken: For encoding text and counting tokens.
    - Langchain OpenAI: For accessing OpenAI embeddings.

Classes:
    Embedding: Class for managing text embeddings and related calculations.
"""

import tiktoken
from langchain_openai import OpenAIEmbeddings

from portfolio_backend.settings import settings


class Embedding:
    """Class for creating embeddings from text and calculating related properties.

    Attributes:
        text (str): The text to be embedded, with newlines replaced by spaces.
        embedding_model (OpenAIEmbeddings): The model used for generating embeddings.

    """

    def __init__(self, text: str, embedding_model: OpenAIEmbeddings | None = None):
        """Initialize the Embedding instance with text and an optional embedding model.

        Args:
            text (str): The text to be embedded.
            embedding_model (OpenAIEmbeddings, optional): An instance of OpenAIEmbeddings.
                If not provided, a default instance is created using settings.
        """
        self.text = text.replace("\n", " ")
        if not embedding_model:
            embedding_model = OpenAIEmbeddings(
                model=settings.embedding_model,
                openai_api_key=settings.openai_api_key,  # type: ignore
            )
        self.embedding_model = embedding_model

    @property
    def tokens_count(self) -> int:
        """Get the number of tokens in the text based on the specified encoding.

        Returns:
            int: The number of tokens in the text after encoding.
        """
        encoding = tiktoken.get_encoding(settings.encoding_name)
        return len(encoding.encode(self.text))

    @property
    def estimated_cost(self) -> float:
        """Calculate the estimated cost of embedding the text based on the token count.

        Returns:
            float: The estimated cost for embedding the text, calculated as
            tokens_count multiplied by the token cost specified in settings.
        """
        return self.tokens_count * settings.token_cost

    @property
    def text_embedding(self) -> list[float]:
        """Generate the embedding for the text using the embedding model.

        Returns:
            list[float]: The generated embedding for the text.
        """
        return self.embedding_model.embed_query(text=self.text)
