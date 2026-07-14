from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState


class Searcher(BaseAgent):
    """
    Searcher Agent - Searches the web for information.
    
    Capabilities:
    - Web search
    - Information retrieval
    - Source gathering
    """
    
    def __init__(self):
        super().__init__("searcher")
    
    def get_system_prompt(self) -> str:
        return """You are a Searcher Agent. Your job is to search for and gather information from the web.

You should:
- Search for relevant information based on the query
- Gather multiple sources when appropriate
- Extract key facts and data
- Provide source references
- Be thorough but efficient

When you find information, summarize it clearly and cite your sources."""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a search task.
        """
        query = task.input_data.get("query", task.description)
        
        system_prompt = self.get_system_prompt()
        
        human_message = f"""Search for information about: {query}

Provide a comprehensive summary of what you find, including:
1. Key facts and information
2. Multiple perspectives if applicable
3. Source references
4. Any relevant data or statistics"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]
        
        # In production, this would use actual web search tools
        # For now, we'll use the LLM's knowledge
        response = await self._call_llm(messages)
        
        return {
            "query": query,
            "results": response,
            "sources": ["LLM Knowledge Base"],  # Placeholder
            "agent": "searcher"
        }
