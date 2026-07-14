"""Qdrant adapter behind a small vector-store interface."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, Filter, PointStruct, VectorParams

from .chunker import DocumentChunk


@dataclass(frozen=True)
class SearchResult:
    """A ranked chunk returned by a vector store."""

    id: str
    content: str
    metadata: dict[str, Any]
    score: float


class VectorStore(Protocol):
    """Interface consumed by retrievers and ingestion pipelines."""

    async def upsert(self, chunks: Sequence[DocumentChunk], vectors: Sequence[Sequence[float]]) -> None: ...
    async def search(self, vector: Sequence[float], limit: int, query_filter: Filter | None = None) -> list[SearchResult]: ...


class QdrantVectorStore:
    """Qdrant implementation. Blocking client calls are isolated from the event loop."""

    def __init__(self, url: str, collection_name: str, dimension: int, client: QdrantClient | None = None) -> None:
        self.collection_name = collection_name
        self.dimension = dimension
        self.client = client or QdrantClient(url=url)
        self._ready = False

    async def ensure_collection(self) -> None:
        if self._ready:
            return
        await asyncio.to_thread(self._ensure_collection)
        self._ready = True

    def _ensure_collection(self) -> None:
        names = {item.name for item in self.client.get_collections().collections}
        if self.collection_name not in names:
            self.client.create_collection(self.collection_name, VectorParams(size=self.dimension, distance=Distance.COSINE))

    async def upsert(self, chunks: Sequence[DocumentChunk], vectors: Sequence[Sequence[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("Every chunk must have one embedding")
        await self.ensure_collection()
        points = [PointStruct(id=str(uuid.uuid5(uuid.NAMESPACE_URL, chunk.id)), vector=list(vector), payload={"content": chunk.content, "metadata": chunk.metadata}) for chunk, vector in zip(chunks, vectors)]
        await asyncio.to_thread(self.client.upsert, collection_name=self.collection_name, points=points)

    async def search(self, vector: Sequence[float], limit: int, query_filter: Filter | None = None) -> list[SearchResult]:
        await self.ensure_collection()
        hits = await asyncio.to_thread(
            self.client.search,
            collection_name=self.collection_name,
            query_vector=list(vector),
            limit=limit,
            query_filter=query_filter,
        )
        return [SearchResult(str(hit.id), str(hit.payload.get("content", "")), dict(hit.payload.get("metadata", {})), float(hit.score)) for hit in hits]
