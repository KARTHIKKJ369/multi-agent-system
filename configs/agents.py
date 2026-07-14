from typing import Dict, List, Any
from enum import Enum


class AgentType(str, Enum):
    SUPERVISOR = "supervisor"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    CODER = "coder"
    TESTER = "tester"
    QA = "qa"
    WRITER = "writer"
    ANALYST = "analyst"
    DEPLOYER = "deployer"


class AgentConfig:
    """Configuration for individual agents"""
    
    def __init__(
        self,
        agent_id: str,
        agent_type: AgentType,
        name: str,
        description: str,
        model: str,
        max_tokens: int = 4000,
        temperature: float = 0.7,
        tools: List[str] = None,
        capabilities: List[str] = None,
    ):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.tools = tools or []
        self.capabilities = capabilities or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type.value,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "tools": self.tools,
            "capabilities": self.capabilities,
        }


# Pre-configured agents
AGENT_REGISTRY: Dict[str, AgentConfig] = {
    # Supervisor
    "supervisor": AgentConfig(
        agent_id="supervisor",
        agent_type=AgentType.SUPERVISOR,
        name="Supervisor",
        description="Orchestrates all agents and coordinates execution",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.3,
        capabilities=["orchestration", "coordination", "retry_logic", "final_approval"],
    ),
    
    # Planning Team
    "planner": AgentConfig(
        agent_id="planner",
        agent_type=AgentType.PLANNER,
        name="Planner",
        description="Analyzes requests and creates execution plans",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.5,
        capabilities=["task_breakdown", "dependency_analysis", "cost_estimation"],
    ),
    
    # Research Team
    "searcher": AgentConfig(
        agent_id="searcher",
        agent_type=AgentType.RESEARCHER,
        name="Searcher",
        description="Searches the web for information",
        model="gpt-4.1-mini",
        max_tokens=2000,
        temperature=0.3,
        tools=["web_search", "duckduckgo"],
        capabilities=["web_search", "information_retrieval"],
    ),
    "retriever": AgentConfig(
        agent_id="retriever",
        agent_type=AgentType.RESEARCHER,
        name="Retriever",
        description="Retrieves documents from knowledge base",
        model="gpt-4.1-mini",
        max_tokens=2000,
        temperature=0.3,
        tools=["vector_search", "document_retrieval"],
        capabilities=["rag", "semantic_search", "document_retrieval"],
    ),
    "summarizer": AgentConfig(
        agent_id="summarizer",
        agent_type=AgentType.RESEARCHER,
        name="Summarizer",
        description="Summarizes research findings",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.5,
        capabilities=["summarization", "synthesis", "extraction"],
    ),
    
    # Coding Team
    "architect": AgentConfig(
        agent_id="architect",
        agent_type=AgentType.CODER,
        name="Architect",
        description="Designs software architecture",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.4,
        capabilities=["architecture_design", "system_design", "tech_stack_selection"],
    ),
    "developer": AgentConfig(
        agent_id="developer",
        agent_type=AgentType.CODER,
        name="Developer",
        description="Writes and implements code",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.2,
        tools=["python", "filesystem", "git"],
        capabilities=["coding", "implementation", "debugging"],
    ),
    "reviewer": AgentConfig(
        agent_id="reviewer",
        agent_type=AgentType.CODER,
        name="Reviewer",
        description="Reviews code for quality and best practices",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.3,
        capabilities=["code_review", "quality_assurance", "best_practices"],
    ),
    "debugger": AgentConfig(
        agent_id="debugger",
        agent_type=AgentType.CODER,
        name="Debugger",
        description="Debugs and fixes issues",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.2,
        tools=["python", "filesystem"],
        capabilities=["debugging", "error_analysis", "fix_generation"],
    ),
    
    # Testing Team
    "unit_tester": AgentConfig(
        agent_id="unit_tester",
        agent_type=AgentType.TESTER,
        name="Unit Tester",
        description="Writes unit tests",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.3,
        tools=["python", "pytest"],
        capabilities=["unit_testing", "test_generation", "coverage"],
    ),
    "integration_tester": AgentConfig(
        agent_id="integration_tester",
        agent_type=AgentType.TESTER,
        name="Integration Tester",
        description="Writes integration tests",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.3,
        capabilities=["integration_testing", "api_testing", "e2e_testing"],
    ),
    
    # QA Team
    "logic_checker": AgentConfig(
        agent_id="logic_checker",
        agent_type=AgentType.QA,
        name="Logic Checker",
        description="Checks for logical consistency",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.2,
        capabilities=["logic_validation", "consistency_check", "reasoning"],
    ),
    "hallucination_detector": AgentConfig(
        agent_id="hallucination_detector",
        agent_type=AgentType.QA,
        name="Hallucination Detector",
        description="Detects hallucinations in AI responses",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.2,
        capabilities=["hallucination_detection", "fact_checking", "verification"],
    ),
    
    # Analytics Team
    "data_analyst": AgentConfig(
        agent_id="data_analyst",
        agent_type=AgentType.ANALYST,
        name="Data Analyst",
        description="Analyzes data and generates insights",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.4,
        tools=["python", "pandas", "sql"],
        capabilities=["data_analysis", "statistics", "insights"],
    ),
    "visualizer": AgentConfig(
        agent_id="visualizer",
        agent_type=AgentType.ANALYST,
        name="Visualizer",
        description="Creates data visualizations",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.4,
        tools=["python", "matplotlib", "plotly"],
        capabilities=["visualization", "charting", "plotting"],
    ),
    
    # Deployment Team
    "docker_agent": AgentConfig(
        agent_id="docker_agent",
        agent_type=AgentType.DEPLOYER,
        name="Docker Agent",
        description="Manages Docker containers and images",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.3,
        tools=["docker", "docker_compose"],
        capabilities=["docker", "containerization", "image_management"],
    ),
    "kubernetes_agent": AgentConfig(
        agent_id="kubernetes_agent",
        agent_type=AgentType.DEPLOYER,
        name="Kubernetes Agent",
        description="Manages Kubernetes deployments",
        model="gpt-4.1-mini",
        max_tokens=3000,
        temperature=0.3,
        tools=["kubectl", "helm"],
        capabilities=["kubernetes", "orchestration", "scaling"],
    ),
    
    # Support Team
    "documentation_writer": AgentConfig(
        agent_id="documentation_writer",
        agent_type=AgentType.WRITER,
        name="Documentation Writer",
        description="Writes technical documentation",
        model="gpt-4.1-mini",
        max_tokens=4000,
        temperature=0.5,
        capabilities=["documentation", "technical_writing", "markdown"],
    ),
}


def get_agent_config(agent_id: str) -> AgentConfig:
    """Get agent configuration by ID"""
    if agent_id not in AGENT_REGISTRY:
        raise ValueError(f"Agent {agent_id} not found in registry")
    return AGENT_REGISTRY[agent_id]


def get_agents_by_type(agent_type: AgentType) -> List[AgentConfig]:
    """Get all agents of a specific type"""
    return [agent for agent in AGENT_REGISTRY.values() if agent.agent_type == agent_type]


def list_all_agents() -> List[AgentConfig]:
    """List all registered agents"""
    return list(AGENT_REGISTRY.values())
