# Memory

Conversation memory is stored in Redis with a TTL. Execution state is cached in Redis and has PostgreSQL persistence hooks. Semantic memory and RAG documents use separate Qdrant collections: `QDRANT_COLLECTION_NAME` and `RAG_COLLECTION_NAME`.

Use `MemoryManager` for conversation or semantic-memory operations. Use `RAGPipeline` for document ingestion and retrieval.
