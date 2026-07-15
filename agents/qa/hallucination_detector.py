from typing import Dict, Any
import json
import re
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
            "clean": self._parse_clean(response),
            "confidence": self._parse_confidence(response),
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
            "clean": self._parse_clean(response),
            "confidence": self._parse_confidence(response),
            "analysis": response
        }

    @staticmethod
    def _payload(content: str) -> Dict[str, Any]:
        match = re.search(r"\{.*?\}", content, re.DOTALL)
        if not match:
            return {}
        try:
            value = json.loads(match.group())
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}

    @classmethod
    def _parse_clean(cls, content: str) -> bool:
        value = cls._payload(content).get("clean")
        if value is None:
            match = re.search(r"\b(?:clean|hallucinations?)\s*[:=-]?\s*(yes|no|true|false|clean)\b", content, re.I)
            value = match.group(1) if match else False
        return str(value).lower() in {"true", "yes", "clean"}

    @classmethod
    def _parse_confidence(cls, content: str) -> float:
        value = cls._payload(content).get("confidence", cls._payload(content).get("score"))
        if value is None:
            match = re.search(r"\b(?:confidence|score)\s*[:=-]?\s*([01](?:\.\d+)?)", content, re.I)
            value = match.group(1) if match else 0.0
        try:
            return max(0.0, min(1.0, float(value)))
        except (TypeError, ValueError):
            return 0.0
