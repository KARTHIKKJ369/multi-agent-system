import asyncio
import json
from collections import defaultdict
from typing import Dict, Optional, List, Any
from datetime import datetime
import redis.asyncio as redis
from sqlalchemy import Column, DateTime, MetaData, String, Table, Text, select, update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .models import ExecutionState, TaskState, AgentState, TaskStatus, AgentStatus
from ..configs.settings import settings
from ..utils.logger import get_logger
from ..utils.observability import observability


class StateManager:
    """Manages execution state with Redis for fast access and PostgreSQL for persistence"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.engine = None
        self.async_session = None
        self._initialized = False
        self._leases = 0
        self._lifecycle_lock = asyncio.Lock()
        self._execution_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._metadata = MetaData()
        self._executions = Table(
            "execution_states", self._metadata,
            Column("execution_id", String(128), primary_key=True),
            Column("state", Text, nullable=False),
            Column("updated_at", DateTime, nullable=False),
        )
        self.logger = get_logger("state_manager")
    
    async def initialize(self) -> None:
        """Initialize connections to Redis and PostgreSQL"""
        async with self._lifecycle_lock:
            if self._initialized:
                self._leases += 1
                return
            self.redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
            self.engine = create_async_engine(settings.postgres_url, echo=settings.debug)
            self.async_session = sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
            async with self.engine.begin() as connection:
                await connection.run_sync(self._metadata.create_all)
            self._initialized = True
            self._leases = 1
            self.logger.info("State manager initialized")
    
    async def close(self) -> None:
        """Close connections"""
        async with self._lifecycle_lock:
            if not self._initialized:
                return
            self._leases -= 1
            if self._leases > 0:
                return
            if self.redis_client:
                await self.redis_client.close()
            if self.engine:
                await self.engine.dispose()
            self.redis_client = self.engine = self.async_session = None
            self._initialized = False
            self._leases = 0
            self._execution_locks.clear()
            self.logger.info("State manager closed")
    
    async def create_execution(self, execution_id: str, user_request: str,
                              conversation_id: Optional[str] = None) -> ExecutionState:
        """Create a new execution state"""
        execution = ExecutionState(
            execution_id=execution_id,
            user_request=user_request,
            conversation_id=conversation_id
        )
        
        # Store in Redis
        await self._store_execution_redis(execution)
        
        # Store in PostgreSQL for persistence
        await self._store_execution_db(execution)
        
        self.logger.info(f"Created execution {execution_id}")
        return execution
    
    async def get_execution(self, execution_id: str) -> Optional[ExecutionState]:
        """Get execution state from Redis"""
        try:
            data = await self.redis_client.get(f"execution:{execution_id}")
            if data:
                execution_dict = json.loads(data)
                return ExecutionState(**execution_dict)
        except Exception as e:
            self.logger.error(f"Error getting execution {execution_id}: {e}")
        
        if self.engine:
            async with self.engine.connect() as connection:
                result = await connection.execute(
                    select(self._executions.c.state).where(self._executions.c.execution_id == execution_id)
                )
                state = result.scalar_one_or_none()
            if state:
                execution = ExecutionState(**json.loads(state))
                await self._store_execution_redis(execution)
                return execution
        return None
    
    async def update_execution(self, execution: ExecutionState) -> None:
        """Update execution state"""
        await self._store_execution_redis(execution)
        await self._store_execution_db(execution)
    
    async def _store_execution_redis(self, execution: ExecutionState) -> None:
        """Store execution in Redis with TTL"""
        data = execution.model_dump_json()
        with observability.span("memory.execution_write", execution_id=execution.execution_id):
            await self.redis_client.setex(
                f"execution:{execution.execution_id}",
                settings.memory_ttl,
                data
            )
    
    async def _store_execution_db(self, execution: ExecutionState) -> None:
        """Store execution in PostgreSQL for long-term persistence"""
        state = execution.model_dump_json()
        values = {"execution_id": execution.execution_id, "state": state, "updated_at": datetime.utcnow()}
        async with self.engine.begin() as connection:
            existing = await connection.execute(
                select(self._executions.c.execution_id).where(self._executions.c.execution_id == execution.execution_id)
            )
            if existing.scalar_one_or_none() is None:
                await connection.execute(self._executions.insert().values(**values))
            else:
                await connection.execute(
                    update(self._executions).where(
                        self._executions.c.execution_id == execution.execution_id
                    ).values(state=values["state"], updated_at=values["updated_at"])
                )
    
    async def add_task(self, execution_id: str, task: TaskState) -> None:
        """Add a task to an execution"""
        await self._mutate_execution(execution_id, lambda execution: execution.add_task(task))
    
    async def update_task(self, execution_id: str, task_id: str,
                         status: TaskStatus,
                         output_data: Optional[Dict] = None,
                         error_message: Optional[str] = None) -> None:
        """Update task status"""
        await self._mutate_execution(
            execution_id,
            lambda execution: execution.update_task_status(task_id, status, output_data, error_message),
        )
    
    async def update_agent(self, execution_id: str, agent_id: str,
                          status: AgentStatus,
                          current_task_id: Optional[str] = None) -> None:
        """Update agent state"""
        await self._mutate_execution(
            execution_id, lambda execution: execution.update_agent_state(agent_id, status, current_task_id)
        )

    async def record_task_metrics(
        self, execution_id: str, task_id: str, tokens: int, cost: float, execution_time: float
    ) -> None:
        def mutate(execution: ExecutionState) -> None:
            task = execution.get_task(task_id)
            if task is None:
                return
            task.tokens_used = tokens
            task.cost = cost
            task.execution_time = execution_time
            execution.total_tokens = sum(item.tokens_used for item in execution.tasks.values())
            execution.total_cost = sum(item.cost for item in execution.tasks.values())
            execution.execution_time = sum(item.execution_time for item in execution.tasks.values())
        await self._mutate_execution(execution_id, mutate)

    async def _mutate_execution(self, execution_id: str, mutation) -> None:
        """Serialize read-modify-write operations for one execution."""
        async with self._execution_locks[execution_id]:
            execution = await self.get_execution(execution_id)
            if execution:
                mutation(execution)
                await self.update_execution(execution)
    
    async def get_ready_tasks(self, execution_id: str) -> List[TaskState]:
        """Get tasks ready for execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            return execution.get_ready_tasks()
        return []
    
    async def is_execution_complete(self, execution_id: str) -> bool:
        """Check if execution is complete"""
        execution = await self.get_execution(execution_id)
        return execution.is_complete() if execution else False
    
    async def get_execution_progress(self, execution_id: str) -> float:
        """Get execution progress"""
        execution = await self.get_execution(execution_id)
        return execution.calculate_progress() if execution else 0.0
    
    async def set_final_response(
        self, execution_id: str, response: str, confidence: Optional[float] = None
    ) -> None:
        """Set final response for execution"""
        def mutate(execution: ExecutionState) -> None:
            execution.final_response = response
            execution.completed_at = datetime.utcnow()
            execution.status = TaskStatus.COMPLETED
            if confidence is not None:
                execution.confidence = confidence
        await self._mutate_execution(execution_id, mutate)
    
    async def store_memory(self, execution_id: str, key: str, value: any) -> None:
        """Store a value in execution memory"""
        await self._mutate_execution(execution_id, lambda execution: execution.memory.__setitem__(key, value))
    
    async def get_memory(self, execution_id: str, key: str) -> Optional[any]:
        """Get a value from execution memory"""
        execution = await self.get_execution(execution_id)
        if execution:
            return execution.memory.get(key)
        return None
    
    async def add_document(self, execution_id: str, document: Dict) -> None:
        """Add a document to execution"""
        await self._mutate_execution(execution_id, lambda execution: execution.documents.append(document))
    
    async def add_artifact(self, execution_id: str, key: str, value: any) -> None:
        """Add an artifact to execution"""
        await self._mutate_execution(execution_id, lambda execution: execution.artifacts.__setitem__(key, value))
    
    async def cleanup_execution(self, execution_id: str) -> None:
        """Clean up execution from Redis (keep in PostgreSQL)"""
        await self.redis_client.delete(f"execution:{execution_id}")
        self.logger.info(f"Cleaned up execution {execution_id} from Redis")


# Global state manager instance
state_manager = StateManager()
