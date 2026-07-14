import asyncio
import json
from typing import Dict, Optional, List
from datetime import datetime
import redis.asyncio as redis
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
        self.logger = get_logger("state_manager")
    
    async def initialize(self) -> None:
        """Initialize connections to Redis and PostgreSQL"""
        # Initialize Redis
        self.redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # Initialize PostgreSQL
        self.engine = create_async_engine(settings.postgres_url, echo=settings.debug)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        self.logger.info("State manager initialized")
    
    async def close(self) -> None:
        """Close connections"""
        if self.redis_client:
            await self.redis_client.close()
        if self.engine:
            await self.engine.dispose()
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
        # TODO: Implement database schema and storage
        pass
    
    async def add_task(self, execution_id: str, task: TaskState) -> None:
        """Add a task to an execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.add_task(task)
            await self.update_execution(execution)
    
    async def update_task(self, execution_id: str, task_id: str,
                         status: TaskStatus,
                         output_data: Optional[Dict] = None,
                         error_message: Optional[str] = None) -> None:
        """Update task status"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.update_task_status(task_id, status, output_data, error_message)
            await self.update_execution(execution)
    
    async def update_agent(self, execution_id: str, agent_id: str,
                          status: AgentStatus,
                          current_task_id: Optional[str] = None) -> None:
        """Update agent state"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.update_agent_state(agent_id, status, current_task_id)
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
    
    async def set_final_response(self, execution_id: str, response: str) -> None:
        """Set final response for execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.final_response = response
            execution.completed_at = datetime.utcnow()
            execution.status = TaskStatus.COMPLETED
            await self.update_execution(execution)
    
    async def store_memory(self, execution_id: str, key: str, value: any) -> None:
        """Store a value in execution memory"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.memory[key] = value
            await self.update_execution(execution)
    
    async def get_memory(self, execution_id: str, key: str) -> Optional[any]:
        """Get a value from execution memory"""
        execution = await self.get_execution(execution_id)
        if execution:
            return execution.memory.get(key)
        return None
    
    async def add_document(self, execution_id: str, document: Dict) -> None:
        """Add a document to execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.documents.append(document)
            await self.update_execution(execution)
    
    async def add_artifact(self, execution_id: str, key: str, value: any) -> None:
        """Add an artifact to execution"""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.artifacts[key] = value
            await self.update_execution(execution)
    
    async def cleanup_execution(self, execution_id: str) -> None:
        """Clean up execution from Redis (keep in PostgreSQL)"""
        await self.redis_client.delete(f"execution:{execution_id}")
        self.logger.info(f"Cleaned up execution {execution_id} from Redis")


# Global state manager instance
state_manager = StateManager()
