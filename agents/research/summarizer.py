from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Summarizer(BaseAgent):
    """
    Summarizer Agent - Summarizes research findings and synthesizes information.
    
    Capabilities:
    - Summarization
    - Synthesis
    - Information extraction
    - Key point identification
    """
    
    def __init__(self):
        super().__init__("summarizer")
    
    def get_system_prompt(self) -> str:
        return """You are a Summarizer Agent. Your job is to summarize and synthesize research findings.

You should:
- Extract key points from research
- Synthesize information from multiple sources
- Create clear, concise summaries
- Identify patterns and themes
- Highlight important findings
- Maintain accuracy while being concise"""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a summarization task.
        """
        content = task.input_data.get("content", task.description)
        sources = task.input_data.get("sources", [])
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Summarize the following research findings:

Content:
{content}

Sources: {sources if sources else 'Not specified'}

Provide:
1. Executive summary (2-3 sentences)
2. Key findings (bullet points)
3. Main themes or patterns
4. Important conclusions
5. Any gaps or limitations"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        response = await self._call_llm(messages)
        
        return {
            "original_content": content,
            "summary": response,
            "sources": sources,
            "agent": "summarizer"
        }
