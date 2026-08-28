from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Literal


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = "multi-agent-system"
    app_version: str = "1.0.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"

    # LLM Providers
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_site_url: Optional[str] = None
    openrouter_app_name: str = "multi-agent-system"
    groq_api_key: Optional[str] = None
    groq_base_url: str = "https://api.groq.com/openai/v1"
    default_llm_provider: Literal["openai", "anthropic", "openrouter", "groq"] = "groq"
    default_model: str = "openai/gpt-oss-120b"

    # Databases
    postgres_url: str = "postgresql+asyncpg://user:password@localhost:5432/multi_agent"
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"

    # Vector Database
    qdrant_collection_name: str = "multi_agent_memory"
    rag_collection_name: str = "multi_agent_rag"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Memory
    memory_ttl: int = 86400
    max_conversation_history: int = 100

    # Task Queue
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # Monitoring
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "multi-agent-system"
    langsmith_tracing: bool = False
    langsmith_api_key: Optional[str] = None
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    structured_logging: bool = True
    metrics_enabled: bool = True
    metrics_path: str = "/metrics/prometheus"
    otel_enabled: bool = False
    otel_service_name: str = "multi-agent-system"
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"

    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Execution
    max_parallel_tasks: int = 10
    task_timeout_seconds: int = 300
    max_retries: int = 3
    retry_delay_seconds: int = 5

    # Human Approval
    require_human_approval: bool = False
    approval_timeout_seconds: int = 300

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5


settings = Settings()
