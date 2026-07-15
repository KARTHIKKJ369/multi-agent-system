"""Shared implementation for registered agents with prompt-only responsibilities."""

from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage

from .base_agent import BaseAgent
from ..state.models import TaskState


class ConfiguredAgent(BaseAgent):
    """Execute a configured specialist task without falling back to an abstract class."""

    prompt = "Complete the assigned task accurately and return a concise, useful result."

    def __init__(self, agent_id: str):
        super().__init__(agent_id)

    def get_system_prompt(self) -> str:
        return self.prompt

    async def execute(self, task: TaskState) -> Dict[str, Any]:
        response = await self._call_llm([
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=f"Task:\n{task.description}\n\nInput:\n{task.input_data}"),
        ])
        return {"task": task.description, "result": response, "agent": self.agent_id}
