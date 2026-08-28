from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uuid

from ..supervisor.supervisor import Supervisor
from ..state.manager import state_manager
from ..configs.settings import settings
from ..utils.logger import get_logger

router = APIRouter()
logger = get_logger("api")


class RequestModel(BaseModel):
    """Model for user requests"""
    message: str = Field(..., description="The user's message or request")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID for context")
    enable_reflection: bool = Field(True, description="Enable reflection loop")
    enable_qa: bool = Field(True, description="Enable QA checks")


class ResponseModel(BaseModel):
    """Model for responses"""
    execution_id: str
    response: str
    execution_time: float
    tasks_completed: int
    total_cost: float
    total_tokens: int
    confidence: float


class ExecutionStatusModel(BaseModel):
    """Model for execution status"""
    execution_id: str
    status: str
    progress: float
    completed_tasks: List[str]
    failed_tasks: List[str]
    total_cost: float
    total_tokens: int


@router.post("/execute", response_model=ResponseModel)
async def execute_request(request: RequestModel) -> ResponseModel:
    """
    Execute a user request through the multi-agent system.
    
    This endpoint:
    1. Creates an execution
    2. Routes to appropriate agents
    3. Executes tasks in parallel when possible
    4. Aggregates results
    5. Returns the final response
    """
    logger.info(f"Received request: {request.message[:100]}...")
    
    try:
        supervisor = Supervisor()
        result = await supervisor.process_request(
            user_request=request.message,
            conversation_id=request.conversation_id,
            enable_reflection=request.enable_reflection,
            enable_qa=request.enable_qa,
        )
        
        return ResponseModel(**result)
        
    except Exception as e:
        err_str = str(e)
        logger.error(f"Error executing request: {err_str}")
        if "429" in err_str or "rate limit" in err_str.lower():
            raise HTTPException(
                status_code=429,
                detail="Upstream LLM Rate Limited (HTTP 429). Free-tier models have low requests-per-minute limits. Please wait 15-30 seconds or configure an OpenAI/Anthropic/OpenRouter key with credits."
            )
        elif "502" in err_str or "overloaded" in err_str.lower():
            raise HTTPException(
                status_code=503,
                detail="Upstream LLM Provider Overloaded (HTTP 502/503). The selected model is temporarily unavailable. Please retry or change DEFAULT_MODEL in .env."
            )
        raise HTTPException(status_code=500, detail=err_str)


@router.get("/execution/{execution_id}", response_model=ExecutionStatusModel)
async def get_execution_status(execution_id: str) -> ExecutionStatusModel:
    """
    Get the status of an execution.
    """
    try:
        execution = await state_manager.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return ExecutionStatusModel(
            execution_id=execution.execution_id,
            status=execution.status.value,
            progress=execution.calculate_progress(),
            completed_tasks=execution.completed_tasks,
            failed_tasks=execution.failed_tasks,
            total_cost=execution.total_cost,
            total_tokens=execution.total_tokens
        )
        
    except Exception as e:
        logger.error(f"Error getting execution status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/execution/{execution_id}/tasks")
async def get_execution_tasks(execution_id: str) -> Dict[str, Any]:
    """
    Get all tasks for an execution.
    """
    try:
        execution = await state_manager.get_execution(execution_id)
        
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        
        return {
            "execution_id": execution_id,
            "tasks": [task.model_dump() for task in execution.tasks.values()]
        }
        
    except Exception as e:
        logger.error(f"Error getting execution tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agents() -> List[Dict[str, Any]]:
    """
    List all available agents.
    """
    try:
        from ..configs.agents import list_all_agents
        agents = list_all_agents()
        
        return [agent.to_dict() for agent in agents]
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str) -> Dict[str, Any]:
    """
    Get information about a specific agent.
    """
    try:
        from ..configs.agents import get_agent_config
        agent = get_agent_config(agent_id)
        
        return agent.to_dict()
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get system metrics.
    """
    try:
        from ..utils.metrics import MetricsCollector
        collector = MetricsCollector()
        
        return collector.metrics.to_dict()
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/stats")
async def get_memory_stats() -> Dict[str, Any]:
    """
    Get memory statistics.
    """
    try:
        from ..memory.manager import memory_manager
        await memory_manager.initialize()
        stats = await memory_manager.get_memory_stats()
        await memory_manager.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/conversation/{conversation_id}/message")
async def store_conversation_message(
    conversation_id: str,
    message: Dict[str, Any]
) -> Dict[str, str]:
    """
    Store a message in conversation memory.
    """
    try:
        from ..memory.manager import memory_manager
        await memory_manager.initialize()
        await memory_manager.store_conversation(conversation_id, message)
        await memory_manager.close()
        
        return {"status": "success", "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Error storing conversation message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str) -> List[Dict[str, Any]]:
    """
    Get conversation history.
    """
    try:
        from ..memory.manager import memory_manager
        await memory_manager.initialize()
        messages = await memory_manager.get_conversation(conversation_id)
        await memory_manager.close()
        
        return messages
        
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def clear_conversation(conversation_id: str) -> Dict[str, str]:
    """
    Clear conversation history.
    """
    try:
        from ..memory.manager import memory_manager
        await memory_manager.initialize()
        await memory_manager.clear_conversation(conversation_id)
        await memory_manager.close()
        
        return {"status": "success", "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))
