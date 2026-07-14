from pathlib import Path

import pytest

from multi_agent_system.rag.chunker import DocumentChunk, TextChunker
from multi_agent_system.rag.document_loader import DocumentLoader, LoadedDocument
from multi_agent_system.rag.rag_pipeline import RAGPipeline
from multi_agent_system.rag.vector_store import SearchResult


class FakeEmbeddings:
    async def embed_documents(self, texts):
        return [[float(len(text))] for text in texts]

    async def embed_query(self, text):
        return [float(len(text))]


class FakeStore:
    def __init__(self):
        self.chunks = []

    async def upsert(self, chunks, vectors):
        self.chunks.extend(chunks)

    async def search(self, vector, limit, query_filter=None):
        return [SearchResult("1", "Useful context", {"source": "guide.md"}, 0.95)][:limit]


def test_chunker_preserves_metadata_and_overlap():
    chunks = TextChunker(10, 2).chunk([LoadedDocument("one two three four", {"source": "guide.md"})])
    assert len(chunks) >= 2
    assert chunks[0].metadata["source"] == "guide.md"
    assert chunks[0].metadata["chunk_index"] == 0


@pytest.mark.asyncio
async def test_pipeline_ingests_and_assembles_context(tmp_path: Path):
    source = tmp_path / "guide.md"
    source.write_text("The system uses Qdrant for vector search.", encoding="utf-8")
    store = FakeStore()
    pipeline = RAGPipeline(DocumentLoader(), TextChunker(100, 10), FakeEmbeddings(), store, 3)

    assert await pipeline.ingest([source]) == 1
    result = await pipeline.retrieve("Which vector database is used?")

    assert "Useful context" in result.context
    assert result.sources[0].metadata["source"] == "guide.md"
