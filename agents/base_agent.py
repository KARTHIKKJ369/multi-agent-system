from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from ..state.models import TaskState
from ..configs.settings import settings
from ..configs.agents import get_agent_config
from ..utils.logger import AgentLogger
from ..utils.metrics import MetricsCollector
from ..utils.observability import observability


class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Every agent must:
    - Be stateless
    - Own its tools
    - Have a specific prompt
    - Perform one specialized task
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.config = get_agent_config(agent_id)
        self.logger = AgentLogger(agent_id)
        self.metrics = MetricsCollector()
        self.last_call_metrics: Dict[str, float] = {"tokens": 0, "cost": 0.0, "latency": 0.0}
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
    
    def _initialize_llm(self):
        """Initialize LLM based on agent configuration"""
        provider = settings.default_llm_provider
        model = settings.default_model if provider == "openrouter" else self.config.model
        
        if provider == "openai":
            return ChatOpenAI(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=settings.openai_api_key
            )
        elif provider == "openrouter":
            headers = {"X-Title": settings.openrouter_app_name}
            if settings.openrouter_site_url:
                headers["HTTP-Referer"] = settings.openrouter_site_url
            return ChatOpenAI(
                model=model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                default_headers=headers,
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=self.config.model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    def _initialize_tools(self) -> Dict[str, Any]:
        """
        Initialize tools for this agent.
        Override in subclasses to add agent-specific tools.
        """
        return {}
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        Must be implemented by each agent.
        """
        pass
    
    @abstractmethod
    async def execute(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute the task.
        Must be implemented by each agent.
        """
        pass
    
    async def _call_llm(
        self,
        messages: List,
        tools: Optional[List] = None
    ) -> str:
        """
        Call the LLM with the given messages.
        """
        start_time = datetime.utcnow()
        
        try:
            with observability.span("llm.call", agent_id=self.agent_id, model=self.config.model):
                if tools:
                    response = await self.llm.ainvoke(messages, tools=tools)
                else:
                    response = await self.llm.ainvoke(messages)
            
            # Calculate metrics
            latency = (datetime.utcnow() - start_time).total_seconds()
            
            # Estimate tokens (rough approximation)
            prompt_text = "\n".join([msg.content for msg in messages])
            prompt_tokens = len(prompt_text.split()) * 1.3  # Rough estimate
            completion_tokens = len(response.content.split()) * 1.3
            total_tokens = int(prompt_tokens + completion_tokens)
            
            # Estimate cost (rough approximation for GPT-4)
            cost = (prompt_tokens * 0.00003 + completion_tokens * 0.00006) / 1000
            
            self.logger.log_llm_call(self.config.model, int(prompt_tokens), int(completion_tokens))
            
            self.metrics.metrics.record_request(
                agent_id=self.agent_id,
                success=True,
                tokens=total_tokens,
                cost=cost,
                latency=latency
            )
            self.last_call_metrics = {"tokens": total_tokens, "cost": cost, "latency": latency}
            
            return response.content
            
        except Exception as e:
            latency = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.metrics.record_request(
                agent_id=self.agent_id,
                success=False,
                tokens=0,
                cost=0.0,
                latency=latency
            )
            self.last_call_metrics = {"tokens": 0, "cost": 0.0, "latency": latency}
            raise
    
    async def _use_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Use a tool by name.
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not available for agent {self.agent_id}")
        
        tool = self.tools[tool_name]
        start_time = datetime.utcnow()
        
        try:
            self.logger.log_tool_call(tool_name, kwargs)
            with observability.span("tool.execution", agent_id=self.agent_id, tool_name=tool_name):
                result = await tool.run(**kwargs)
            latency = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.log_tool_result(tool_name, str(result)[:200])
            self.metrics.metrics.record_tool_call(tool_name, True, latency)
            
            return result
            
        except Exception as e:
            latency = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.metrics.record_tool_call(tool_name, False, latency)
            raise
    
    def get_capabilities(self) -> List[str]:
        """Get the capabilities of this agent"""
        return self.config.capabilities
    
    def get_tools(self) -> List[str]:
        """Get the available tools for this agent"""
        return self.config.tools
