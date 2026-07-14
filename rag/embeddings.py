"""Embedding-provider interfaces and OpenAI implementation."""

from __future__ import annotations

from typing import Protocol, Sequence


class EmbeddingProvider(Protocol):
    """Interface that lets applications replace an embedding vendor."""

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


class OpenAIEmbeddingProvider:
    """OpenAI embeddings adapter with lazy client construction."""

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        """Create the SDK adapter only when embeddings are actually requested."""
        if self._client is None:
            from langchain_openai import OpenAIEmbeddings
            self._client = OpenAIEmbeddings(model=self.model, api_key=self.api_key)
        return self._client

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return await self.client.aembed_documents(list(texts))

    async def embed_query(self, text: str) -> list[float]:
        return await self.client.aembed_query(text)
