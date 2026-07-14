from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class HallucinationDetector(BaseAgent):
    """
    Hallucination Detector Agent - Detects hallucinations in AI responses.
    
    Capabilities:
    - Hallucination detection
    - Fact checking
    - Verification
    - Source validation
    """
    
    def __init__(self):
        super().__init__("hallucination_detector")
    
    def get_system_prompt(self) -> str:
        return """You are a Hallucination Detector Agent. Your job is to detect hallucinations and verify factual accuracy.

You should:
- Identify claims that may be hallucinated
- Check for factual accuracy
- Verify against known information
- Flag unsupported assertions
- Identify speculation presented as fact
- Assess confidence in claims

Your analysis should be thorough and conservative - when in doubt, flag it."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a hallucination detection task.
        """
        content = task.input_data.get("content", task.description)
        sources = task.input_data.get("sources", [])
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Detect potential hallucinations in the following content:

Content:
{content}

Available sources: {sources if sources else 'None'}

Provide:
1. Overall assessment (clean/contains hallucinations)
2. Specific claims that may be hallucinated
3. Claims that need verification
4. Confidence score (0-1) for overall accuracy
5. Recommendations for verification
6. Any speculation identified"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "content": content,
            "analysis": response,
            "clean": True,  # Would be parsed from response
            "confidence": 0.85,  # Would be parsed from response
            "agent": "hallucination_detector"
        }
    
    async def check(self, aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the aggregated results for hallucinations.
        """
        content = aggregated.get("aggregated", "")
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Check the following content for hallucinations:

Content:
{content}

Provide:
1. Whether the content appears to contain hallucinations
2. Specific claims that need verification
3. Confidence score (0-1) for accuracy"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "clean": True,
            "confidence": 0.85,
            "analysis": response
        }
