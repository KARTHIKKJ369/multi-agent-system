from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseTool(ABC):
    """
    Base class for all tools.
    
    Every tool must:
    - Have a name and description
    - Implement the run method
    - Be independently testable
    - Handle errors gracefully
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """
        Execute the tool with the given arguments.
        
        Must be implemented by each tool.
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the tool schema for LLM function calling.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the parameters schema.
        Override in subclasses to define specific parameters.
        """
        return {
            "type": "object",
            "properties": {},
            "required": []
        }
    
    async def validate_inputs(self, **kwargs) -> bool:
        """
        Validate input parameters.
        Override in subclasses for custom validation.
        """
        return True
    
    def __repr__(self) -> str:
        return f"Tool(name={self.name}, description={self.description})"
