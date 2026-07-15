import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, select, update
from sqlalchemy.ext.asyncio import create_async_engine
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

from .types import MemoryType, MemoryPriority
from ..configs.settings import settings
from ..utils.logger import get_logger
from ..utils.observability import observability
from ..rag.embeddings import OpenAIEmbeddingProvider


class MemoryManager:
    """
    Manages all memory operations across different storage backends.
    
    Architecture:
    - Conversation Memory: Redis (fast, short-term)
    - Long-term Memory: PostgreSQL (persistent)
    - Semantic Memory: Qdrant (vector search)
    - User Memory: PostgreSQL (user preferences)
    - Knowledge Memory: Qdrant (knowledge base)
    """
    
    def __init__(self):
        self.logger = get_logger("memory_manager")
        self.redis_client: Optional[redis.Redis] = None
        self.qdrant_client: Optional[QdrantClient] = None
        self.engine = None
        self.embedding_provider = OpenAIEmbeddingProvider(settings.embedding_model, settings.openai_api_key)
        self._initialized = False
        self._leases = 0
        self._lifecycle_lock = asyncio.Lock()
        self._metadata = MetaData()
        self._long_term_memory = Table(
            "long_term_memory", self._metadata,
            Column("key", String(512), primary_key=True),
            Column("category", String(128), nullable=False),
            Column("value", Text, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
        self._user_preferences = Table(
            "user_preferences", self._metadata,
            Column("user_id", String(256), primary_key=True),
            Column("preference_key", String(256), primary_key=True),
            Column("value", Text, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
    
    async def initialize(self) -> None:
        """Initialize all memory backends"""
        async with self._lifecycle_lock:
            if self._initialized:
                self._leases += 1
                return
            self.redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            self.qdrant_client = QdrantClient(url=settings.qdrant_url)
            self.engine = create_async_engine(settings.postgres_url, echo=settings.debug)
            async with self.engine.begin() as connection:
                await connection.run_sync(self._metadata.create_all)
            await self._ensure_qdrant_collection()
            self._initialized = True
            self._leases = 1
            self.logger.info("Memory manager initialized")
    
    async def close(self) -> None:
        """Close all connections"""
        async with self._lifecycle_lock:
            if not self._initialized:
                return
            self._leases -= 1
            if self._leases > 0:
                return
            if self.redis_client:
                await self.redis_client.close()
            if self.qdrant_client:
                self.qdrant_client.close()
            if self.engine:
                await self.engine.dispose()
            self.redis_client = self.qdrant_client = self.engine = None
            self._initialized = False
            self._leases = 0
            self.logger.info("Memory manager closed")
    
    async def _ensure_qdrant_collection(self) -> None:
        """Ensure Qdrant collection exists"""
        collections = self.qdrant_client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if settings.qdrant_collection_name not in collection_names:
            self.qdrant_client.create_collection(
                collection_name=settings.qdrant_collection_name,
                vectors_config=VectorParams(
                    size=settings.embedding_dimension,
                    distance=Distance.COSINE
                )
            )
            self.logger.info(f"Created Qdrant collection: {settings.qdrant_collection_name}")
    
    # Conversation Memory (Redis)
    
    async def store_conversation(
        self,
        conversation_id: str,
        message: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store a conversation message in Redis"""
        if not self._initialized:
            await self.initialize()
        
        key = f"conversation:{conversation_id}"
        ttl = ttl or settings.memory_ttl
        
        # Get existing messages
        messages = await self.redis_client.lrange(key, 0, -1)
        
        # Add new message
        messages.append(json.dumps(message))
        
        # Keep only recent messages
        if len(messages) > settings.max_conversation_history:
            messages = messages[-settings.max_conversation_history:]
        
        # Store back
        with observability.span("memory.conversation_write", conversation_id=conversation_id):
            await self.redis_client.delete(key)
            for msg in messages:
                await self.redis_client.rpush(key, msg)
            await self.redis_client.expire(key, ttl)
        self.logger.debug(f"Stored conversation message for {conversation_id}")
    
    async def get_conversation(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history from Redis"""
        if not self._initialized:
            await self.initialize()
        
        key = f"conversation:{conversation_id}"
        with observability.span("memory.conversation_read", conversation_id=conversation_id):
            messages = await self.redis_client.lrange(key, 0, -1)
        
        return [json.loads(msg) for msg in messages]
    
    async def clear_conversation(self, conversation_id: str) -> None:
        """Clear conversation history"""
        if not self._initialized:
            await self.initialize()
        
        key = f"conversation:{conversation_id}"
        await self.redis_client.delete(key)
        self.logger.debug(f"Cleared conversation {conversation_id}")
    
    # Semantic Memory (Qdrant)
    
    async def store_embedding(
        self,
        vector: List[float],
        payload: Dict[str, Any],
        point_id: Optional[str] = None
    ) -> str:
        """Store a vector embedding in Qdrant"""
        if not self._initialized:
            await self.initialize()
        
        if point_id is None:
            point_id = f"{datetime.utcnow().timestamp()}"
        
        point = PointStruct(
            id=point_id,
            vector=vector,
            payload=payload
        )
        
        self.qdrant_client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=[point]
        )
        
        self.logger.debug(f"Stored embedding with ID {point_id}")
        return point_id
    
    async def search_embeddings(
        self,
        query_vector: List[float],
        limit: int = 5,
        filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings"""
        if not self._initialized:
            await self.initialize()
        
        search_filter = None
        if filters:
            conditions = [
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
                for key, value in filters.items()
            ]
            search_filter = Filter(must=conditions)
        
        with observability.span("memory.vector_search", collection=settings.qdrant_collection_name):
            results = self.qdrant_client.search(
                collection_name=settings.qdrant_collection_name,
                query_vector=query_vector,
                limit=limit,
                query_filter=search_filter
            )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload
            }
            for hit in results
        ]
    
    async def delete_embedding(self, point_id: str) -> None:
        """Delete an embedding by ID"""
        if not self._initialized:
            await self.initialize()
        
        self.qdrant_client.delete(
            collection_name=settings.qdrant_collection_name,
            points_selector=[point_id]
        )
        
        self.logger.debug(f"Deleted embedding {point_id}")
    
    # Long-term Memory (PostgreSQL)
    
    async def store_long_term(
        self,
        key: str,
        value: Any,
        category: str = "general"
    ) -> None:
        """Store long-term memory in PostgreSQL."""
        if not self._initialized:
            await self.initialize()
        values = {"key": key, "category": category, "value": json.dumps(value), "updated_at": datetime.utcnow()}
        async with self.engine.begin() as connection:
            existing = await connection.execute(select(self._long_term_memory.c.key).where(self._long_term_memory.c.key == key))
            if existing.scalar_one_or_none() is None:
                await connection.execute(self._long_term_memory.insert().values(**values))
            else:
                await connection.execute(update(self._long_term_memory).where(self._long_term_memory.c.key == key).values(**values))
    
    async def get_long_term(self, key: str) -> Optional[Any]:
        """Retrieve long-term memory from PostgreSQL."""
        if not self._initialized:
            await self.initialize()
        async with self.engine.connect() as connection:
            result = await connection.execute(select(self._long_term_memory.c.value).where(self._long_term_memory.c.key == key))
            value = result.scalar_one_or_none()
        return json.loads(value) if value is not None else None
    
    # User Memory
    
    async def store_user_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any
    ) -> None:
        """Store a user preference in PostgreSQL."""
        if not self._initialized:
            await self.initialize()
        values = {
            "user_id": user_id, "preference_key": preference_key,
            "value": json.dumps(preference_value), "updated_at": datetime.utcnow(),
        }
        async with self.engine.begin() as connection:
            statement = select(self._user_preferences.c.user_id).where(
                self._user_preferences.c.user_id == user_id,
                self._user_preferences.c.preference_key == preference_key,
            )
            existing = await connection.execute(statement)
            if existing.scalar_one_or_none() is None:
                await connection.execute(self._user_preferences.insert().values(**values))
            else:
                await connection.execute(update(self._user_preferences).where(
                    self._user_preferences.c.user_id == user_id,
                    self._user_preferences.c.preference_key == preference_key,
                ).values(**values))
    
    async def get_user_preference(
        self,
        user_id: str,
        preference_key: str
    ) -> Optional[Any]:
        """Get a user preference from PostgreSQL."""
        if not self._initialized:
            await self.initialize()
        async with self.engine.connect() as connection:
            result = await connection.execute(select(self._user_preferences.c.value).where(
                self._user_preferences.c.user_id == user_id,
                self._user_preferences.c.preference_key == preference_key,
            ))
            value = result.scalar_one_or_none()
        return json.loads(value) if value is not None else None
    
    # Knowledge Base
    
    async def add_to_knowledge_base(
        self,
        text: str,
        metadata: Dict[str, Any],
        embedding: Optional[List[float]] = None
    ) -> str:
        """Add document to knowledge base"""
        if not self._initialized:
            await self.initialize()
        
        if embedding is None:
            embedding = await self.embedding_provider.embed_query(text)
        
        payload = {
            "text": text,
            "metadata": metadata,
            "type": "knowledge",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return await self.store_embedding(embedding, payload)
    
    async def search_knowledge_base(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search knowledge base"""
        if not self._initialized:
            await self.initialize()
        
        return await self.search_embeddings(
            query_vector,
            limit=limit,
            filters={"type": "knowledge"}
        )
    
    # Utility methods
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about memory usage"""
        if not self._initialized:
            await self.initialize()
        
        # Redis stats
        redis_info = await self.redis_client.info("memory")
        
        # Qdrant stats
        collection_info = self.qdrant_client.get_collection(
            settings.qdrant_collection_name
        )
        
        return {
            "redis_used_memory": redis_info.get("used_memory_human", "unknown"),
            "qdrant_points_count": collection_info.points_count,
            "qdrant_vector_count": collection_info.vectors_count,
        }


# Global memory manager instance
memory_manager = MemoryManager()
