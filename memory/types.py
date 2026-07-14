from enum import Enum


class MemoryType(str, Enum):
    """Types of memory storage"""
    CONVERSATION = "conversation"  # Short-term, Redis
    LONG_TERM = "long_term"  # Persistent, PostgreSQL
    SEMANTIC = "semantic"  # Vector embeddings, Qdrant
    USER = "user"  # User preferences, PostgreSQL
    KNOWLEDGE = "knowledge"  # Knowledge base, Qdrant


class MemoryPriority(str, Enum):
    """Priority levels for memory items"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
