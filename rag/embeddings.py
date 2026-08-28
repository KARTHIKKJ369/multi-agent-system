import hashlib
from typing import Protocol, Sequence
import numpy as np


class EmbeddingProvider(Protocol):
    """Interface that lets applications replace an embedding vendor."""

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


class FallbackEmbeddingProvider:
    """Fallback deterministic embeddings when no OpenAI API key is configured."""

    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _hash_vector(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.default_rng(seed)
        vec = rng.standard_normal(self.dimension)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    async def aembed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._hash_vector(t) for t in texts]

    async def aembed_query(self, text: str) -> list[float]:
        return self._hash_vector(text)


class OpenAIEmbeddingProvider:
    """OpenAI embeddings adapter with lazy client construction and graceful fallback."""

    def __init__(self, model: str, api_key: str | None = None) -> None:
        self.model = model
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        """Create the SDK adapter or fallback provider."""
        if self._client is None:
            if not self.api_key:
                from ..configs.settings import settings
                self.api_key = settings.openai_api_key
            if not self.api_key:
                self._client = FallbackEmbeddingProvider()
            else:
                try:
                    from langchain_openai import OpenAIEmbeddings
                    self._client = OpenAIEmbeddings(model=self.model, api_key=self.api_key)
                except Exception:
                    self._client = FallbackEmbeddingProvider()
        return self._client

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return await self.client.aembed_documents(list(texts))

    async def embed_query(self, text: str) -> list[float]:
        return await self.client.aembed_query(text)
