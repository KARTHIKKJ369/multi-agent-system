import time
from typing import Dict, Optional
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Metrics:
    """Metrics tracking for agent operations"""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    total_latency: float = 0.0
    retry_count: int = 0
    
    # Per-agent metrics
    agent_metrics: Dict[str, Dict] = field(default_factory=lambda: defaultdict(dict))
    
    # Per-tool metrics
    tool_metrics: Dict[str, Dict] = field(default_factory=lambda: defaultdict(dict))
    
    def record_request(self, agent_id: str, success: bool, tokens: int, 
                       cost: float, latency: float) -> None:
        """Record a request"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_tokens += tokens
        self.total_cost += cost
        self.total_latency += latency
        
        # Update agent-specific metrics
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = {
                "requests": 0,
                "successes": 0,
                "failures": 0,
                "tokens": 0,
                "cost": 0.0,
                "latency": 0.0,
            }
        
        self.agent_metrics[agent_id]["requests"] += 1
        if success:
            self.agent_metrics[agent_id]["successes"] += 1
        else:
            self.agent_metrics[agent_id]["failures"] += 1
        self.agent_metrics[agent_id]["tokens"] += tokens
        self.agent_metrics[agent_id]["cost"] += cost
        self.agent_metrics[agent_id]["latency"] += latency
    
    def record_tool_call(self, tool_name: str, success: bool, latency: float) -> None:
        """Record a tool call"""
        if tool_name not in self.tool_metrics:
            self.tool_metrics[tool_name] = {
                "calls": 0,
                "successes": 0,
                "failures": 0,
                "latency": 0.0,
            }
        
        self.tool_metrics[tool_name]["calls"] += 1
        if success:
            self.tool_metrics[tool_name]["successes"] += 1
        else:
            self.tool_metrics[tool_name]["failures"] += 1
        self.tool_metrics[tool_name]["latency"] += latency
    
    def record_retry(self) -> None:
        """Record a retry attempt"""
        self.retry_count += 1
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests
    
    def get_average_latency(self) -> float:
        """Calculate average latency"""
        if self.total_requests == 0:
            return 0.0
        return self.total_latency / self.total_requests
    
    def get_average_tokens(self) -> float:
        """Calculate average tokens per request"""
        if self.total_requests == 0:
            return 0.0
        return self.total_tokens / self.total_requests
    
    def get_agent_metrics(self, agent_id: str) -> Optional[Dict]:
        """Get metrics for a specific agent"""
        return self.agent_metrics.get(agent_id)
    
    def get_tool_metrics(self, tool_name: str) -> Optional[Dict]:
        """Get metrics for a specific tool"""
        return self.tool_metrics.get(tool_name)
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary"""
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.get_success_rate(),
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "average_latency": self.get_average_latency(),
            "average_tokens": self.get_average_tokens(),
            "retry_count": self.retry_count,
            "agent_metrics": dict(self.agent_metrics),
            "tool_metrics": dict(self.tool_metrics),
        }


class MetricsCollector:
    """Singleton metrics collector"""
    
    _instance: Optional["MetricsCollector"] = None
    _metrics: Metrics
    
    def __new__(cls) -> "MetricsCollector":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._metrics = Metrics()
        return cls._instance
    
    @property
    def metrics(self) -> Metrics:
        return self._metrics
    
    def reset(self) -> None:
        """Reset all metrics"""
        self._metrics = Metrics()
