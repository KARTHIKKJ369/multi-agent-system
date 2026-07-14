# Architecture

The API receives a request, the supervisor creates a task graph, and the router selects specialised agents. State is held in Redis for fast reads and designed for PostgreSQL persistence; conversation memory uses Redis and semantic knowledge uses Qdrant.

```mermaid
flowchart LR
  Client --> API[FastAPI]
  API --> Supervisor
  Supervisor --> Graph[Task graph]
  Graph --> Agents
  Agents --> Tools
  Agents --> RAG
  RAG --> Qdrant
  Supervisor --> Redis
  Supervisor --> Postgres
```

Components communicate through small interfaces: `BaseAgent`, `BaseTool`, `EmbeddingProvider`, and `VectorStore`. This keeps LLM providers and RAG backends replaceable.
