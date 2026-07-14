from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Developer(BaseAgent):
    """
    Developer Agent - Writes and implements code.
    
    Capabilities:
    - Coding
    - Implementation
    - Code generation
    - Bug fixing
    - Refactoring
    """
    
    def __init__(self):
        super().__init__("developer")
    
    def get_system_prompt(self) -> str:
        return """You are a Developer Agent. Your job is to write high-quality, production-ready code.

You should:
- Write clean, readable, and maintainable code
- Follow best practices and coding standards
- Include appropriate error handling
- Add comments where necessary
- Write efficient and performant code
- Consider edge cases
- Follow the provided specifications exactly

Your code should be production-ready and well-documented."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a development task.
        """
        specification = task.input_data.get("specification", task.description)
        language = task.input_data.get("language", "python")
        context = task.input_data.get("context", {})
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Write code for the following specification:

Specification:
{specification}

Language: {language}

Context:
{context if context else 'None'}

Provide:
1. The complete, runnable code
2. Brief explanation of the implementation
3. Any dependencies or requirements
4. Usage examples if applicable"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "specification": specification,
            "code": response,
            "language": language,
            "context": context,
            "agent": "developer"
        }
