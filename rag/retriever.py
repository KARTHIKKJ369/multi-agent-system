"""Embedding-backed document retrieval."""

from __future__ import annotations

from typing import Sequence

from .embeddings import EmbeddingProvider
from .vector_store import SearchResult, VectorStore


class Retriever:
    """Retrieve chunks through interfaces instead of agent-specific code."""

    def __init__(self, embeddings: EmbeddingProvider, vector_store: VectorStore, top_k: int) -> None:
        self.embeddings = embeddings
        self.vector_store = vector_store
        self.top_k = top_k

    async def retrieve(self, query: str, limit: int | None = None) -> list[SearchResult]:
        """Embed a query and return its most relevant source chunks."""
        return await self.vector_store.search(await self.embeddings.embed_query(query), limit or self.top_k)
