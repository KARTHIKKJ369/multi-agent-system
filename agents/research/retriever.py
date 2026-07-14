from typing import Dict, Any, List
from langchain_core.messages import HumanMessage, SystemMessage

from ..base_agent import BaseAgent
from ...state.models import TaskState
from ...configs.settings import settings
from ...rag.rag_pipeline import RAGPipeline


class Retriever(BaseAgent):
    """
    Retriever Agent - Retrieves documents from knowledge base using RAG.
    
    Capabilities:
    - Semantic search
    - Document retrieval
    - Context extraction
    - RAG implementation
    """
    
    def __init__(self, rag_pipeline: RAGPipeline | None = None):
        super().__init__("retriever")
        self.rag_pipeline = rag_pipeline or RAGPipeline.from_settings(settings)
    
    def get_system_prompt(self) -> str:
        return """You are a Retriever Agent. Your job is to retrieve relevant documents from the knowledge base and extract context.

You should:
- Understand the user's query
- Retrieve relevant documents using semantic search
- Extract the most relevant information
- Provide context that helps answer the query
- Cite the sources of your information"""
    
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a retrieval task.
        """
        query = task.input_data.get("query", task.description)
        
        result = await self.rag_pipeline.retrieve(query)
        return {
            "query": query,
            "context": result.context,
            "sources": [source.metadata for source in result.sources],
            "agent": "retriever"
        }
