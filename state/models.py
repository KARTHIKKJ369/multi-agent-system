from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class AgentStatus(str, Enum):
    """Status of an agent"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class TaskState(BaseModel):
    """State of a single task"""
    task_id: str
    agent_id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    input_data: Dict[str, Any] = Field(default_factory=dict)
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    dependencies: List[str] = Field(default_factory=list)
    child_tasks: List[str] = Field(default_factory=list)
    parent_task: Optional[str] = None
    confidence: float = 0.0
    tokens_used: int = 0
    cost: float = 0.0
    execution_time: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class AgentState(BaseModel):
    """State of an agent"""
    agent_id: str
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    total_tasks_completed: int = 0
    total_tasks_failed: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    last_activity: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ExecutionState(BaseModel):
    """State of an entire execution"""
    execution_id: str
    user_request: str
    conversation_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    tasks: Dict[str, TaskState] = Field(default_factory=dict)
    agents: Dict[str, AgentState] = Field(default_factory=dict)
    completed_tasks: List[str] = Field(default_factory=list)
    failed_tasks: List[str] = Field(default_factory=list)
    active_agent: Optional[str] = None
    memory: Dict[str, Any] = Field(default_factory=dict)
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    total_cost: float = 0.0
    total_tokens: int = 0
    execution_time: float = 0.0
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    final_response: Optional[str] = None
    
    class Config:
        use_enum_values = True
    
    def add_task(self, task: TaskState) -> None:
        """Add a task to the execution"""
        self.tasks[task.task_id] = task
    
    def get_task(self, task_id: str) -> Optional[TaskState]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                           output_data: Optional[Dict] = None,
                           error_message: Optional[str] = None) -> None:
        """Update task status"""
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = status
            if output_data:
                task.output_data = output_data
            if error_message:
                task.error_message = error_message
            
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
                if task_id not in self.completed_tasks:
                    self.completed_tasks.append(task_id)
            elif status == TaskStatus.FAILED:
                if task_id not in self.failed_tasks:
                    self.failed_tasks.append(task_id)
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get agent state"""
        return self.agents.get(agent_id)
    
    def update_agent_state(self, agent_id: str, status: AgentStatus,
                          current_task_id: Optional[str] = None) -> None:
        """Update agent state"""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentState(agent_id=agent_id)
        
        agent = self.agents[agent_id]
        agent.status = status
        agent.current_task_id = current_task_id
        agent.last_activity = datetime.utcnow()
        
        if status == AgentStatus.IDLE:
            agent.current_task_id = None
    
    def get_ready_tasks(self) -> List[TaskState]:
        """Get tasks that are ready to execute (dependencies satisfied)"""
        ready_tasks = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                dependencies_met = all(
                    dep in self.completed_tasks for dep in task.dependencies
                )
                if dependencies_met:
                    ready_tasks.append(task)
        return ready_tasks
    
    def get_failed_tasks(self) -> List[TaskState]:
        """Get all failed tasks"""
        return [task for task in self.tasks.values() if task.status == TaskStatus.FAILED]
    
    def is_complete(self) -> bool:
        """Check if execution is complete"""
        return all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
            for task in self.tasks.values()
        )
    
    def calculate_progress(self) -> float:
        """Calculate execution progress (0.0 to 1.0)"""
        if not self.tasks:
            return 0.0
        completed = len(self.completed_tasks)
        total = len(self.tasks)
        return completed / total if total > 0 else 0.0
