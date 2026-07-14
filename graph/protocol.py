from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in the communication protocol"""
    TASK_ASSIGNMENT = "task_assignment"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    TASK_FAILED = "task_failed"
    AGENT_STATUS = "agent_status"
    HEARTBEAT = "heartbeat"
    CONTROL = "control"


class AgentMessage(BaseModel):
    """
    Standard message format for agent communication.
    
    Every message includes:
    - Task ID
    - Agent Name
    - Timestamp
    - Parent Task
    - Child Tasks
    - Confidence
    - Output
    - Dependencies
    - Status
    """
    message_id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    message_type: MessageType
    task_id: str
    agent_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parent_task: Optional[str] = None
    child_tasks: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    output: Optional[Dict[str, Any]] = None
    dependencies: List[str] = Field(default_factory=list)
    status: str = "pending"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """Create message from dictionary"""
        return cls(**data)


class TaskAssignmentMessage(AgentMessage):
    """Message for assigning a task to an agent"""
    
    def __init__(
        self,
        task_id: str,
        agent_name: str,
        task_description: str,
        input_data: Dict[str, Any],
        dependencies: List[str] = None,
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.TASK_ASSIGNMENT,
            task_id=task_id,
            agent_name=agent_name,
            dependencies=dependencies or [],
            **kwargs
        )
        self.task_description = task_description
        self.input_data = input_data


class TaskUpdateMessage(AgentMessage):
    """Message for updating task status"""
    
    def __init__(
        self,
        task_id: str,
        agent_name: str,
        status: str,
        progress: float = 0.0,
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.TASK_UPDATE,
            task_id=task_id,
            agent_name=agent_name,
            status=status,
            **kwargs
        )
        self.progress = progress


class TaskCompleteMessage(AgentMessage):
    """Message for task completion"""
    
    def __init__(
        self,
        task_id: str,
        agent_name: str,
        output: Dict[str, Any],
        confidence: float = 0.9,
        tokens_used: int = 0,
        execution_time: float = 0.0,
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.TASK_COMPLETE,
            task_id=task_id,
            agent_name=agent_name,
            output=output,
            confidence=confidence,
            status="completed",
            **kwargs
        )
        self.tokens_used = tokens_used
        self.execution_time = execution_time


class TaskFailedMessage(AgentMessage):
    """Message for task failure"""
    
    def __init__(
        self,
        task_id: str,
        agent_name: str,
        error_message: str,
        retry_count: int = 0,
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.TASK_FAILED,
            task_id=task_id,
            agent_name=agent_name,
            status="failed",
            **kwargs
        )
        self.error_message = error_message
        self.retry_count = retry_count


class AgentStatusMessage(AgentMessage):
    """Message for agent status updates"""
    
    def __init__(
        self,
        agent_name: str,
        status: str,
        current_task: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message_type=MessageType.AGENT_STATUS,
            task_id=current_task or "status",
            agent_name=agent_name,
            status=status,
            **kwargs
        )
        self.current_task = current_task


class MessageBroker:
    """
    Message broker for handling agent communication.
    
    In production, this would use a message queue like RabbitMQ, Kafka, or Redis Pub/Sub.
    For now, we'll use an in-memory implementation.
    """
    
    def __init__(self):
        self.message_handlers: Dict[MessageType, List] = {}
        self.message_history: List[AgentMessage] = []
    
    def subscribe(self, message_type: MessageType, handler) -> None:
        """Subscribe to a specific message type"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
    
    def unsubscribe(self, message_type: MessageType, handler) -> None:
        """Unsubscribe from a message type"""
        if message_type in self.message_handlers:
            self.message_handlers[message_type].remove(handler)
    
    async def publish(self, message: AgentMessage) -> None:
        """Publish a message to all subscribers"""
        self.message_history.append(message)
        
        handlers = self.message_handlers.get(message.message_type, [])
        for handler in handlers:
            try:
                await handler(message)
            except Exception as e:
                print(f"Error in message handler: {e}")
    
    def get_message_history(self, task_id: Optional[str] = None) -> List[AgentMessage]:
        """Get message history, optionally filtered by task_id"""
        if task_id:
            return [msg for msg in self.message_history if msg.task_id == task_id]
        return self.message_history.copy()
    
    def clear_history(self) -> None:
        """Clear message history"""
        self.message_history.clear()


# Global message broker instance
message_broker = MessageBroker()
