"""Text chunking with stable chunk metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .document_loader import LoadedDocument


@dataclass(frozen=True)
class DocumentChunk:
    """A retrievable section of a loaded document."""

    id: str
    content: str
    metadata: dict[str, Any]


class TextChunker:
    """Split documents on character boundaries, preferring whitespace."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        if chunk_size <= 0 or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_size must be positive and greater than chunk_overlap")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, documents: Iterable[LoadedDocument]) -> list[DocumentChunk]:
        """Return overlapping chunks while retaining source metadata."""
        chunks: list[DocumentChunk] = []
        for document_index, document in enumerate(documents):
            text, start, chunk_index = document.content.strip(), 0, 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                if end < len(text):
                    boundary = text.rfind(" ", start, end)
                    if boundary > start:
                        end = boundary
                content = text[start:end].strip()
                if content:
                    chunks.append(DocumentChunk(
                        id=f"{document.metadata.get('source', document_index)}:{chunk_index}",
                        content=content,
                        metadata={**document.metadata, "chunk_index": chunk_index, "char_start": start},
                    ))
                    chunk_index += 1
                if end >= len(text):
                    break
                start = max(end - self.chunk_overlap, start + 1)
        return chunks
