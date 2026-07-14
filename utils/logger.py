import logging
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
from ..configs.settings import settings


class JsonFormatter(logging.Formatter):
    """Emit log records as JSON for production log aggregation."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_to_file: bool = True,
    log_to_console: bool = True,
) -> None:
    """Setup logging configuration for the application"""
    
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = JsonFormatter() if settings.structured_logging else logging.Formatter(
        fmt="%(levelname)s - %(message)s"
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
    
    # File handler - general logs
    if log_to_file:
        today = datetime.now().strftime("%Y-%m-%d")
        file_handler = logging.FileHandler(
            log_path / f"app_{today}.log",
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler(
            log_path / f"error_{today}.log",
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)


class AgentLogger:
    """Specialized logger for agent operations"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = get_logger(f"agent.{agent_id}")
    
    def log_task_start(self, task_id: str, task_description: str) -> None:
        """Log task start"""
        self.logger.info(
            f"[{self.agent_id}] Task {task_id} started: {task_description}"
        )
    
    def log_task_complete(self, task_id: str, duration: float, tokens_used: int) -> None:
        """Log task completion"""
        self.logger.info(
            f"[{self.agent_id}] Task {task_id} completed in {duration:.2f}s, "
            f"tokens used: {tokens_used}"
        )
    
    def log_task_error(self, task_id: str, error: str) -> None:
        """Log task error"""
        self.logger.error(
            f"[{self.agent_id}] Task {task_id} failed: {error}"
        )
    
    def log_tool_call(self, tool_name: str, args: dict) -> None:
        """Log tool invocation"""
        self.logger.debug(
            f"[{self.agent_id}] Tool called: {tool_name} with args: {args}"
        )
    
    def log_tool_result(self, tool_name: str, result: str) -> None:
        """Log tool result"""
        self.logger.debug(
            f"[{self.agent_id}] Tool result: {tool_name} - {result[:200]}..."
        )
    
    def log_llm_call(self, model: str, prompt_tokens: int, completion_tokens: int) -> None:
        """Log LLM API call"""
        self.logger.debug(
            f"[{self.agent_id}] LLM call: {model}, "
            f"prompt_tokens: {prompt_tokens}, completion_tokens: {completion_tokens}"
        )
    
    def log_memory_operation(self, operation: str, key: str) -> None:
        """Log memory operation"""
        self.logger.debug(
            f"[{self.agent_id}] Memory {operation}: {key}"
        )
    
    def log_retry(self, task_id: str, attempt: int, max_retries: int) -> None:
        """Log retry attempt"""
        self.logger.warning(
            f"[{self.agent_id}] Task {task_id} retry {attempt}/{max_retries}"
        )
