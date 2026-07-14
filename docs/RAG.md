# RAG Pipeline

`rag/` is deliberately independent of the agent layer:

1. `DocumentLoader` reads TXT, Markdown, PDF, and DOCX files.
2. `TextChunker` creates overlapping, source-tagged chunks.
3. `EmbeddingProvider` generates vectors (OpenAI by default).
4. `QdrantVectorStore` upserts and searches chunks.
5. `RAGPipeline` assembles source-labelled context.

```python
pipeline = RAGPipeline.from_settings(settings)
await pipeline.ingest(["docs/handbook.md"])
result = await pipeline.retrieve("How does routing work?")
```

Inject fake or alternate implementations of `EmbeddingProvider` and `VectorStore` for tests or provider changes.
