from typing import Dict, Optional, List
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage

from ..configs.agents import get_agent_config, list_all_agents, AgentType
from ..configs.settings import settings
from ..utils.logger import get_logger


class Router:
    """
    Router - Chooses the best agent for a given task.
    
    Uses LLM-based routing to determine which agent should handle a request.
    """
    
    def __init__(self):
        self.logger = get_logger("router")
        self.llm = self._initialize_llm()
        self.agent_cache: Dict[str, str] = {}
    
    def _initialize_llm(self):
        """Initialize LLM for routing decisions"""
        if settings.default_llm_provider == "openai":
            return ChatOpenAI(
                model="gpt-4.1-mini",  # Use faster model for routing
                temperature=0.1,
                api_key=settings.openai_api_key
            )
        elif settings.default_llm_provider == "openrouter":
            headers = {"X-Title": settings.openrouter_app_name}
            if settings.openrouter_site_url:
                headers["HTTP-Referer"] = settings.openrouter_site_url
            return ChatOpenAI(
                model=settings.default_model,
                temperature=0.1,
                api_key=settings.openrouter_api_key,
                base_url=settings.openrouter_base_url,
                default_headers=headers,
            )
        elif settings.default_llm_provider == "anthropic":
            return ChatAnthropic(
                model="claude-3-haiku",
                temperature=0.1,
                api_key=settings.anthropic_api_key
            )
        else:
            raise ValueError(f"Unknown LLM provider: {settings.default_llm_provider}")
    
    def get_agent(self, agent_id: str):
        """Get an agent instance by ID"""
        # Import agent classes dynamically
        agent_classes = {
            "searcher": ("agents.research.searcher", "Searcher"),
            "retriever": ("agents.research.retriever", "Retriever"),
            "summarizer": ("agents.research.summarizer", "Summarizer"),
            "architect": ("agents.coding.architect", "Architect"),
            "developer": ("agents.coding.developer", "Developer"),
            "reviewer": ("agents.coding.reviewer", "Reviewer"),
            "debugger": ("agents.coding.debugger", "Debugger"),
            "unit_tester": ("agents.testing.unit_tester", "UnitTester"),
            "integration_tester": ("agents.testing.integration_tester", "IntegrationTester"),
            "logic_checker": ("agents.qa.logic_checker", "LogicChecker"),
            "hallucination_detector": ("agents.qa.hallucination_detector", "HallucinationDetector"),
            "data_analyst": ("agents.analytics.data_analyst", "DataAnalyst"),
            "visualizer": ("agents.analytics.visualizer", "Visualizer"),
            "docker_agent": ("agents.deployment.docker_agent", "DockerAgent"),
            "kubernetes_agent": ("agents.deployment.kubernetes_agent", "KubernetesAgent"),
            "documentation_writer": ("agents.support.documentation_writer", "DocumentationWriter"),
        }
        
        if agent_id not in agent_classes:
            raise ValueError(f"Unknown agent ID: {agent_id}")
        
        module_name, class_name = agent_classes[agent_id]
        
        import importlib
        try:
            try:
                module = importlib.import_module(f"multi_agent_system.{module_name}")
            except ImportError:
                try:
                    module = importlib.import_module(module_name)
                except ImportError:
                    module = importlib.import_module(f"..{module_name}", package="multi_agent_system.routing")
            agent_class = getattr(module, class_name)
            return agent_class()
        except Exception as exc:
            raise RuntimeError(f"Agent implementation for {agent_id} is unavailable: {exc}") from exc
    
    async def route(self, task_description: str, context: Optional[Dict] = None) -> str:
        """
        Route a task to the appropriate agent.
        
        Args:
            task_description: Description of the task
            context: Additional context for routing
            
        Returns:
            Agent ID to handle the task
        """
        # Check cache first
        cache_key = f"{task_description}:{str(context)}"
        if cache_key in self.agent_cache:
            return self.agent_cache[cache_key]
        
        # Get all available agents
        agents = list_all_agents()
        agent_descriptions = "\n".join([
            f"- {agent.agent_id}: {agent.description} (capabilities: {', '.join(agent.capabilities)})"
            for agent in agents
        ])
        
        system_prompt = f"""You are a task router. Your job is to determine which agent should handle a given task.

Available agents:
{agent_descriptions}

Analyze the task and return only the agent_id that should handle it. Choose the most specific agent for the task."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Task: {task_description}\nContext: {context or 'None'}")
        ]
        
        response = await self.llm.ainvoke(messages)
        agent_id = response.content.strip().lower()
        
        # Validate agent_id
        valid_agent_ids = [agent.agent_id for agent in agents]
        if agent_id not in valid_agent_ids:
            self.logger.warning(f"LLM returned invalid agent_id: {agent_id}, defaulting to developer")
            agent_id = "developer"
        
        # Cache the result
        self.agent_cache[cache_key] = agent_id
        
        self.logger.info(f"Routed task to agent: {agent_id}")
        return agent_id
    
    def route_by_type(self, task_type: str) -> str:
        """
        Route based on task type (simpler, rule-based routing).
        
        Args:
            task_type: Type of task (research, coding, analysis, etc.)
            
        Returns:
            Agent ID to handle the task
        """
        routing_rules = {
            "research": "searcher",
            "search": "searcher",
            "information": "retriever",
            "summarize": "summarizer",
            "coding": "developer",
            "code": "developer",
            "architecture": "architect",
            "design": "architect",
            "review": "reviewer",
            "debug": "debugger",
            "test": "unit_tester",
            "testing": "unit_tester",
            "qa": "logic_checker",
            "analysis": "data_analyst",
            "data": "data_analyst",
            "visualization": "visualizer",
            "chart": "visualizer",
            "deploy": "docker_agent",
            "deployment": "docker_agent",
            "kubernetes": "kubernetes_agent",
            "k8s": "kubernetes_agent",
            "documentation": "documentation_writer",
            "docs": "documentation_writer",
            "write": "documentation_writer",
        }
        
        # Check for partial matches
        for key, agent_id in routing_rules.items():
            if key in task_type.lower():
                return agent_id
        
        # Default to developer
        return "developer"
    
    def get_team_agents(self, team_name: str) -> List[str]:
        """
        Get all agents belonging to a specific team.
        
        Args:
            team_name: Name of the team (research, coding, testing, etc.)
            
        Returns:
            List of agent IDs
        """
        team_mappings = {
            "planning": ["planner"],
            "research": ["searcher", "retriever", "summarizer"],
            "coding": ["architect", "developer", "reviewer", "debugger"],
            "testing": ["unit_tester", "integration_tester"],
            "qa": ["logic_checker", "hallucination_detector"],
            "analytics": ["data_analyst", "visualizer"],
            "deployment": ["docker_agent", "kubernetes_agent"],
            "support": ["documentation_writer"],
        }
        
        return team_mappings.get(team_name.lower(), [])
    
    async def route_to_team(self, task_description: str, team_name: str) -> str:
        """
        Route a task to the best agent within a specific team.
        
        Args:
            task_description: Description of the task
            team_name: Name of the team
            
        Returns:
            Agent ID to handle the task
        """
        team_agents = self.get_team_agents(team_name)
        
        if not team_agents:
            self.logger.warning(f"No agents found for team: {team_name}")
            return "developer"
        
        if len(team_agents) == 1:
            return team_agents[0]
        
        # Use LLM to choose the best agent within the team
        agent_descriptions = "\n".join([
            f"- {agent_id}: {get_agent_config(agent_id).description}"
            for agent_id in team_agents
        ])
        
        system_prompt = f"""You are a team router. Choose the best agent from this team for the task.

Team: {team_name}
Available agents:
{agent_descriptions}

Return only the agent_id."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Task: {task_description}")
        ]
        
        response = await self.llm.ainvoke(messages)
        agent_id = response.content.strip().lower()
        
        if agent_id not in team_agents:
            agent_id = team_agents[0]
        
        return agent_id
