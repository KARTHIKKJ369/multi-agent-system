from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState, TaskStatus
from ...graph.task_graph import TaskGraph
from ...utils.logger import AgentLogger


class Planner(BaseAgent):
    """
    Planner Agent - Analyzes requests and creates execution plans.
    
    Responsibilities:
    - Analyze request
    - Estimate complexity
    - Break into subtasks
    - Identify dependencies
    - Estimate cost
    """
    
    def __init__(self):
        super().__init__("planner")
    
    def get_system_prompt(self) -> str:
        return """You are a Planner Agent. Your job is to analyze user requests and create detailed execution plans.

For each request, you should:
1. Understand the goal
2. Break it down into specific, actionable subtasks
3. Identify dependencies between tasks
4. Assign each task to the appropriate agent
5. Estimate complexity and resources needed

Available agents:
- searcher: Web search and information retrieval
- retriever: Document retrieval from knowledge base
- summarizer: Summarize research findings
- architect: Design software architecture
- developer: Write and implement code
- reviewer: Review code for quality
- debugger: Debug and fix issues
- unit_tester: Write unit tests
- integration_tester: Write integration tests
- logic_checker: Check logical consistency
- hallucination_detector: Detect hallucinations
- data_analyst: Analyze data
- visualizer: Create visualizations
- docker_agent: Manage Docker containers
- kubernetes_agent: Manage Kubernetes deployments
- documentation_writer: Write documentation

Output format:
Provide a JSON object with:
- goal: The main goal
- tasks: List of tasks with:
  - task_id: Unique identifier
  - agent: Which agent should handle it
  - description: What the task does
  - dependencies: List of task_ids this task depends on
  - priority: high, medium, or low
  - estimated_tokens: Estimated token usage
  - estimated_time: Estimated time in seconds"""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute the planning task.
        """
        user_request = task.input_data.get("user_request", "")
        approach = task.input_data.get("approach", "general")
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Create an execution plan for this request:
Request: {user_request}
Approach: {approach}

Respond with a JSON object following the specified format."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        # Parse the response to extract the plan
        # In production, this would use proper JSON parsing with error handling
        plan = self._parse_plan(response)
        
        return plan
    
    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """
        Parse the LLM response into a structured plan.
        """
        import json
        import re
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                plan = json.loads(json_match.group())
                return plan
            except json.JSONDecodeError:
                pass
        
        # Fallback: create a simple plan
        return {
            "goal": "Execute user request",
            "tasks": [
                {
                    "task_id": str(uuid.uuid4()),
                    "agent": "developer",
                    "description": "Process the request",
                    "dependencies": [],
                    "priority": "high",
                    "estimated_tokens": 1000,
                    "estimated_time": 30
                }
            ]
        }
    
    async def create_plan(
        self,
        user_request: str,
        approach: str
    ) -> TaskGraph:
        """
        Create a task graph from a user request.
        """
        task = TaskState(
            task_id=str(uuid.uuid4()),
            agent_id="planner",
            description="Create execution plan",
            input_data={
                "user_request": user_request,
                "approach": approach
            }
        )
        
        plan = await self.execute(task)
        
        # Convert plan to TaskGraph
        task_graph = TaskGraph()
        
        for task_data in plan.get("tasks", []):
            task_state = TaskState(
                task_id=task_data["task_id"],
                agent_id=task_data["agent"],
                description=task_data["description"],
                dependencies=task_data.get("dependencies", []),
                input_data={
                    "estimated_tokens": task_data.get("estimated_tokens", 1000),
                    "estimated_time": task_data.get("estimated_time", 30),
                    "priority": task_data.get("priority", "medium")
                }
            )
            task_graph.add_task(task_state)
        
        return task_graph
    
    def estimate_complexity(self, user_request: str) -> str:
        """
        Estimate the complexity of a request.
        Returns: simple, moderate, or complex
        """
        # Simple heuristic based on request length and keywords
        complexity_indicators = [
            "multiple", "several", "various", "integrate", "system",
            "architecture", "comprehensive", "detailed", "analysis"
        ]
        
        request_lower = user_request.lower()
        indicator_count = sum(1 for indicator in complexity_indicators if indicator in request_lower)
        
        if indicator_count >= 3 or len(user_request) > 500:
            return "complex"
        elif indicator_count >= 1 or len(user_request) > 200:
            return "moderate"
        else:
            return "simple"
