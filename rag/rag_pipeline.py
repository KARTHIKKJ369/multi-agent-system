"""Composable ingestion and context-assembly workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .chunker import DocumentChunk, TextChunker
from .document_loader import DocumentLoader
from .embeddings import EmbeddingProvider, OpenAIEmbeddingProvider
from .retriever import Retriever
from .vector_store import QdrantVectorStore, SearchResult, VectorStore


@dataclass(frozen=True)
class RAGResult:
    """Context and source records suitable for an agent prompt."""

    query: str
    context: str
    sources: list[SearchResult]


class RAGPipeline:
    """Independent RAG facade for ingestion and retrieval consumers."""

    def __init__(self, loader: DocumentLoader, chunker: TextChunker, embeddings: EmbeddingProvider, vector_store: VectorStore, top_k: int) -> None:
        self.loader, self.chunker, self.embeddings, self.vector_store = loader, chunker, embeddings, vector_store
        self.retriever = Retriever(embeddings, vector_store, top_k)

    @classmethod
    def from_settings(cls, settings) -> "RAGPipeline":
        """Build the default OpenAI/Qdrant implementation from application settings."""
        return cls(DocumentLoader(), TextChunker(settings.chunk_size, settings.chunk_overlap), OpenAIEmbeddingProvider(settings.embedding_model, settings.openai_api_key), QdrantVectorStore(settings.qdrant_url, settings.rag_collection_name, settings.embedding_dimension), settings.top_k_results)

    async def ingest(self, paths: Iterable[str | Path]) -> int:
        """Load, chunk, embed, and upsert documents; returns indexed chunk count."""
        chunks = self.chunker.chunk(await self.loader.load_many(paths))
        if chunks:
            await self.vector_store.upsert(chunks, await self.embeddings.embed_documents([chunk.content for chunk in chunks]))
        return len(chunks)

    async def retrieve(self, query: str, limit: int | None = None) -> RAGResult:
        """Retrieve sources and assemble citation-ready context."""
        sources = await self.retriever.retrieve(query, limit)
        context = "\n\n".join(f"[Source {index}: {source.metadata.get('source', source.id)}]\n{source.content}" for index, source in enumerate(sources, start=1))
        return RAGResult(query=query, context=context, sources=sources)
