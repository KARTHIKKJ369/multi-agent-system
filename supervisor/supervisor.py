import asyncio
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..state.models import ExecutionState, TaskState, TaskStatus, AgentStatus
from ..state.manager import state_manager
from ..configs.settings import settings
from ..configs.agents import get_agent_config, AgentType
from ..utils.logger import AgentLogger, get_logger
from ..utils.metrics import MetricsCollector
from ..routing.router import Router
from ..graph.task_graph import TaskGraph
from ..utils.observability import observability


class Supervisor:
    """
    Supervisor Agent - Orchestrates all agents and coordinates execution.
    
    Responsibilities:
    - Understand user request
    - Create execution plan
    - Delegate work
    - Retry failures
    - Merge outputs
    - Approve final answer
    
    Supervisor NEVER performs work directly.
    Supervisor ONLY coordinates.
    """
    
    def __init__(self):
        self.logger = get_logger("supervisor")
        self.agent_logger = AgentLogger("supervisor")
        self.metrics = MetricsCollector()
        self.router = Router()
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        if settings.default_llm_provider == "openai":
            return ChatOpenAI(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.openai_api_key
            )
        elif settings.default_llm_provider == "openrouter":
            headers = {"X-Title": settings.openrouter_app_name}
            if settings.openrouter_site_url:
                headers["HTTP-Referer"] = settings.openrouter_site_url
            return ChatOpenAI(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                default_headers=headers,
            )
        elif settings.default_llm_provider == "groq":
            return ChatOpenAI(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.groq_api_key,
                base_url=settings.groq_base_url,
                max_retries=6,
            )
        elif settings.default_llm_provider == "anthropic":
            return ChatAnthropic(
                model=settings.default_model,
                temperature=0.3,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unknown LLM provider: {settings.default_llm_provider}")
    
    async def process_request(
        self,
        user_request: str,
        conversation_id: Optional[str] = None,
        enable_reflection: bool = True,
        enable_qa: bool = True,
    ) -> Dict[str, Any]:
        """
        Process a user request through the multi-agent system.
        
        Args:
            user_request: The user's request
            conversation_id: Optional conversation ID for context
            
        Returns:
            Dict containing the final response and metadata
        """
        execution_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        self.logger.info(f"Processing request {execution_id}: {user_request[:100]}...")
        
        try:
            with observability.span("supervisor.execution", execution_id=execution_id):
                # Initialize state
                await state_manager.initialize()
                execution = await state_manager.create_execution(
                execution_id=execution_id,
                user_request=user_request,
                conversation_id=conversation_id
            )
                execution.started_at = start_time
            
            # Step 1: Analyze request and determine approach
                approach = await self._analyze_request(user_request)
                self.logger.info(f"Approach determined: {approach}")
            
            # Step 2: Create execution plan using Planner
                from ..agents.planner.planner import Planner
                planner = Planner()
                task_graph = await planner.create_plan(user_request, approach)
            
            # Step 3: Execute tasks through the graph
                results = await self._execute_task_graph(execution_id, task_graph)
            
            # Step 4: Aggregate results
                aggregated = await self._aggregate_results(results)
            
            # Step 5: Reflection and QA
                validated = await self._reflect_and_validate(
                    user_request, aggregated, enable_reflection=enable_reflection, enable_qa=enable_qa
                )
            
            # Step 6: Generate final response
                final_response = await self._generate_final_response(user_request, validated)
            
            # Store final response
                await state_manager.set_final_response(
                    execution_id, final_response, confidence=validated["confidence"]
                )
                execution = await state_manager.get_execution(execution_id) or execution
            
                execution_time = (datetime.utcnow() - start_time).total_seconds()
            
                return {
                "execution_id": execution_id,
                "response": final_response,
                "execution_time": execution_time,
                "tasks_completed": len(execution.completed_tasks),
                "total_cost": execution.total_cost,
                "total_tokens": execution.total_tokens,
                "confidence": execution.confidence
                }
            
        except Exception as e:
            self.logger.error(f"Error processing request {execution_id}: {e}")
            raise
        finally:
            await state_manager.close()
    
    async def _call_llm_with_retry(self, messages: List[Any], max_retries: int = 4) -> Any:
        """Call LLM with exponential backoff retry for rate limits (429)"""
        for attempt in range(max_retries):
            try:
                return await self.llm.ainvoke(messages)
            except Exception as e:
                err_str = str(e).lower()
                if ("429" in err_str or "rate limit" in err_str or "overloaded" in err_str or "502" in err_str) and attempt < max_retries - 1:
                    wait_time = (2 ** (attempt + 1)) + 1
                    self.logger.warning(f"Rate limited or overloaded, retrying in {wait_time}s... (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async def _analyze_request(self, user_request: str) -> str:
        """
        Analyze the user request to determine the best approach.
        
        Returns the type of task (e.g., "research", "coding", "analysis", "general")
        """
        system_prompt = """You are a request analyzer. Determine the type of task based on the user request.
        
Possible task types:
- research: Information gathering, fact-finding, literature review
- coding: Writing code, debugging, software development
- analysis: Data analysis, statistics, business intelligence
- writing: Content creation, documentation, reports
- deployment: Infrastructure, DevOps, cloud deployment
- general: General questions, advice, explanations

Respond with only the task type."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_request)
        ]
        
        response = await self._call_llm_with_retry(messages)
        task_type = response.content.strip().lower()
        
        return task_type
    
    async def _execute_task_graph(
        self,
        execution_id: str,
        task_graph: TaskGraph
    ) -> Dict[str, Any]:
        """
        Execute tasks through the dependency graph.
        
        Handles parallel execution when dependencies allow.
        """
        results = {}
        # The state store is the source for the API.  Register the complete graph
        # before tasks run so status and metric updates cannot silently be dropped.
        for task in task_graph.tasks.values():
            await state_manager.add_task(execution_id, task)
        with observability.span("graph.execution", execution_id=execution_id):
            while not task_graph.is_complete():
                # Get ready tasks (dependencies satisfied)
                ready_tasks = task_graph.get_ready_tasks()
                
                if not ready_tasks:
                    # Check for deadlock
                    if task_graph.has_pending_tasks():
                        self.logger.error("Deadlock detected in task graph")
                        break
                    continue
                
                # Execute ready tasks with rate limit pacing
                tasks_to_execute = ready_tasks
                execution_results = []
                for task in tasks_to_execute:
                    try:
                        res = await self._execute_single_task(execution_id, task)
                        execution_results.append(res)
                    except Exception as e:
                        execution_results.append(e)
                    await asyncio.sleep(0.5)
                
                # Process results
                for task, result in zip(tasks_to_execute, execution_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Task {task.task_id} failed: {result}")
                        task_graph.mark_failed(task.task_id)
                    else:
                        results[task.task_id] = result
                        task_graph.mark_completed(task.task_id)
        
        return results
    
    async def _execute_single_task(
        self,
        execution_id: str,
        task: TaskState
    ) -> Dict[str, Any]:
        """
        Execute a single task by routing to the appropriate agent.
        """
        # Update task status
        await state_manager.update_task(
            execution_id, task.task_id, TaskStatus.IN_PROGRESS
        )
        
        # Update agent state
        await state_manager.update_agent(
            execution_id, task.agent_id, AgentStatus.BUSY, task.task_id
        )
        
        self.agent_logger.log_task_start(task.task_id, task.description)
        started_at = datetime.utcnow()
        
        try:
            # Get the appropriate agent
            agent = self.router.get_agent(task.agent_id)
            
            # Execute the task
            with observability.span("agent.execution", execution_id=execution_id, agent_id=task.agent_id, task_id=task.task_id):
                result = await agent.execute(task)

            usage = getattr(agent, "last_call_metrics", {})
            await state_manager.record_task_metrics(
                execution_id,
                task.task_id,
                int(usage.get("tokens", 0)),
                float(usage.get("cost", 0.0)),
                (datetime.utcnow() - started_at).total_seconds(),
            )
            
            # Update task with results
            await state_manager.update_task(
                execution_id,
                task.task_id,
                TaskStatus.COMPLETED,
                output_data=result
            )
            
            # Update agent state
            await state_manager.update_agent(
                execution_id, task.agent_id, AgentStatus.IDLE
            )
            
            self.agent_logger.log_task_complete(
                task.task_id,
                task.execution_time,
                task.tokens_used
            )
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            await state_manager.update_task(
                execution_id,
                task.task_id,
                TaskStatus.FAILED,
                error_message=error_msg
            )
            
            await state_manager.update_agent(
                execution_id, task.agent_id, AgentStatus.ERROR
            )
            
            self.agent_logger.log_task_error(task.task_id, error_msg)
            
            # Implement retry logic
            if task.retry_count < task.max_retries:
                return await self._retry_task(execution_id, task)
            
            raise
    
    async def _retry_task(self, execution_id: str, task: TaskState) -> Dict[str, Any]:
        """
        Retry a failed task with exponential backoff.
        """
        task.retry_count += 1
        delay = settings.retry_delay_seconds * (2 ** task.retry_count)
        
        self.agent_logger.log_retry(task.task_id, task.retry_count, task.max_retries)
        self.metrics.metrics.record_retry()
        
        await asyncio.sleep(delay)
        
        # Update task status to retrying
        await state_manager.update_task(
            execution_id, task.task_id, TaskStatus.RETRYING
        )
        
        # Try executing again
        return await self._execute_single_task(execution_id, task)
    
    async def _aggregate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate results from multiple tasks into a coherent output.
        """
        system_prompt = """You are a result aggregator. Combine the outputs from multiple agents into a coherent response.
        
Organize the information logically, remove redundancies, and ensure consistency."""
        
        results_text = "\n\n".join([
            f"Task {task_id}:\n{result}" for task_id, result in results.items()
        ])
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Aggregate these results:\n\n{results_text}")
        ]
        
        response = await self._call_llm_with_retry(messages)
        
        return {"aggregated": response.content, "raw_results": results}
    
    async def _reflect_and_validate(
        self,
        user_request: str,
        aggregated: Dict[str, Any],
        enable_reflection: bool = True,
        enable_qa: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform reflection and quality assurance on the aggregated results.
        """
        content = aggregated["aggregated"]
        if enable_reflection:
            from ..graph.reflection import ReflectionLoop
            reflection = await ReflectionLoop().reflect(user_request, content)
            content = reflection["final_output"]
            aggregated = {**aggregated, "aggregated": content}

        if enable_qa:
            from ..agents.qa.logic_checker import LogicChecker
            from ..agents.qa.hallucination_detector import HallucinationDetector
            logic_result = await LogicChecker().validate(user_request, aggregated)
            hallucination_result = await HallucinationDetector().check(aggregated)
        else:
            logic_result = {"valid": True, "confidence": 1.0}
            hallucination_result = {"clean": True, "confidence": 1.0}
        
        return {
            "content": content,
            "logic_valid": logic_result["valid"],
            "hallucination_free": hallucination_result["clean"],
            "confidence": (logic_result["confidence"] + hallucination_result["confidence"]) / 2
        }
    
    async def _generate_final_response(
        self,
        user_request: str,
        validated: Dict[str, Any]
    ) -> str:
        """
        Generate the final response to the user.
        """
        system_prompt = """You are the final response generator. Create a clear, helpful response to the user based on the validated results.
        
Be concise but thorough. Use markdown formatting when appropriate."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User request: {user_request}\n\nValidated results: {validated['content']}")
        ]
        
        response = await self._call_llm_with_retry(messages)
        return response.content
