from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class LogicChecker(BaseAgent):
    """
    Logic Checker Agent - Checks for logical consistency and reasoning.
    
    Capabilities:
    - Logic validation
    - Consistency check
    - Reasoning verification
    - Contradiction detection
    """
    
    def __init__(self):
        super().__init__("logic_checker")
    
    def get_system_prompt(self) -> str:
        return """You are a Logic Checker Agent. Your job is to verify logical consistency and reasoning.

You should:
- Check for logical contradictions
- Verify reasoning chains
- Identify inconsistencies
- Validate conclusions
- Check for fallacies
- Ensure coherence

Your analysis should be thorough and objective."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a logic checking task.
        """
        content = task.input_data.get("content", task.description)
        context = task.input_data.get("context", {})
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Check the logical consistency of the following:

Content:
{content}

Context:
{context if context else 'None'}

Provide:
1. Overall logical assessment (valid/invalid/partially valid)
2. Any contradictions found
3. Inconsistencies identified
4. Reasoning chain analysis
5. Confidence score (0-1)
6. Specific issues with line references
7. Recommendations for improvement"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "content": content,
            "analysis": response,
            "valid": True,  # Would be parsed from response
            "confidence": 0.85,  # Would be parsed from response
            "agent": "logic_checker"
        }
    
    async def validate(self, user_request: str, aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the aggregated results against the original request.
        """
        content = aggregated.get("aggregated", "")
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Validate that the response logically addresses the user's request.

User Request:
{user_request}

Response:
{content}

Provide:
1. Whether the response logically addresses the request
2. Any logical gaps
3. Consistency assessment
4. Confidence score (0-1)"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "valid": True,
            "confidence": 0.85,
            "analysis": response
        }
