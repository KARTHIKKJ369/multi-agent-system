from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Architect(BaseAgent):
    """
    Architect Agent - Designs software architecture and system design.
    
    Capabilities:
    - Architecture design
    - System design
    - Tech stack selection
    - Component design
    - API design
    """
    
    def __init__(self):
        super().__init__("architect")
    
    def get_system_prompt(self) -> str:
        return """You are an Architect Agent. Your job is to design software architecture and systems.

You should:
- Understand requirements thoroughly
- Design scalable and maintainable architecture
- Select appropriate technologies
- Define component boundaries
- Design APIs and interfaces
- Consider performance, security, and reliability
- Document architectural decisions

Your designs should follow best practices and industry standards."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute an architecture task.
        """
        requirements = task.input_data.get("requirements", task.description)
        constraints = task.input_data.get("constraints", {})
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Design the architecture for the following requirements:

Requirements:
{requirements}

Constraints:
{constraints if constraints else 'None specified'}

Provide:
1. High-level architecture overview
2. Component breakdown
3. Technology stack recommendations
4. Data flow diagram (described in text)
5. API design (if applicable)
6. Security considerations
7. Scalability considerations
8. Deployment strategy"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "requirements": requirements,
            "architecture": response,
            "constraints": constraints,
            "agent": "architect"
        }
