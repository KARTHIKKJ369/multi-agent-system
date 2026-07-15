import asyncio
from types import SimpleNamespace

import pytest

from multi_agent_system.agents.base_agent import BaseAgent
from multi_agent_system.api.routes import RequestModel, execute_request
from multi_agent_system.graph.reflection import ReflectionLoop
from multi_agent_system.graph.task_graph import TaskGraph
from multi_agent_system.routing.router import Router
from multi_agent_system.state.manager import StateManager
from multi_agent_system.state.models import TaskState, TaskStatus
from multi_agent_system.supervisor.supervisor import Supervisor
from multi_agent_system.memory.manager import MemoryManager


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.closed = False

    async def setex(self, key, ttl, value):
        self.values[key] = value

    async def get(self, key):
        return self.values.get(key)

    async def delete(self, key):
        self.values.pop(key, None)

    async def close(self):
        self.closed = True


class FakeResult:
    def __init__(self, value=None):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeConnection:
    def __init__(self):
        self.statements = []

    async def execute(self, statement):
        self.statements.append(statement)
        return FakeResult()


class FakeTransaction:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(self, *args):
        return None


class FakeEngine:
    def __init__(self):
        self.connection = FakeConnection()

    def begin(self):
        return FakeTransaction(self.connection)

    def connect(self):
        return FakeTransaction(self.connection)

    async def dispose(self):
        return None


@pytest.mark.asyncio
async def test_state_mutations_are_serialized_and_task_metrics_are_persisted(monkeypatch):
    manager = StateManager()
    manager.redis_client = FakeRedis()
    manager._initialized = True

    async def no_db_write(execution):
        return None

    monkeypatch.setattr(manager, "_store_execution_db", no_db_write)
    await manager.create_execution("run", "request")
    await manager.add_task("run", TaskState(task_id="one", agent_id="developer", description="one"))
    await manager.add_task("run", TaskState(task_id="two", agent_id="developer", description="two"))

    await asyncio.gather(
        manager.update_task("run", "one", TaskStatus.COMPLETED),
        manager.update_task("run", "two", TaskStatus.COMPLETED),
        manager.record_task_metrics("run", "one", 10, 0.1, 1.0),
        manager.record_task_metrics("run", "two", 20, 0.2, 2.0),
    )

    execution = await manager.get_execution("run")
    assert set(execution.completed_tasks) == {"one", "two"}
    assert execution.total_tokens == 30
    assert execution.total_cost == pytest.approx(0.3)
    await manager.set_final_response("run", "done", confidence=0.8)
    execution = await manager.get_execution("run")
    assert execution.confidence == 0.8


@pytest.mark.asyncio
async def test_shared_state_manager_does_not_close_until_final_lease():
    manager = StateManager()
    redis = FakeRedis()
    manager.redis_client = redis
    manager._initialized = True
    manager._leases = 2
    manager.engine = FakeEngine()

    await manager.close()
    assert manager._initialized is True
    assert redis.closed is False
    await manager.close()
    assert manager._initialized is False
    assert redis.closed is True


@pytest.mark.asyncio
async def test_postgres_persistence_paths_write_execution_and_memory_records():
    manager = StateManager()
    manager.engine = FakeEngine()
    from multi_agent_system.state.models import ExecutionState
    await manager._store_execution_db(ExecutionState(execution_id="persisted", user_request="request"))
    assert len(manager.engine.connection.statements) == 2  # existence check and insert

    memory = MemoryManager()
    memory._initialized = True
    memory.engine = FakeEngine()
    await memory.store_long_term("key", {"value": 1})
    await memory.store_user_preference("user", "theme", "dark")
    assert len(memory.engine.connection.statements) == 4  # check and insert for each record


@pytest.mark.asyncio
async def test_knowledge_base_uses_a_real_embedding_when_none_is_supplied(monkeypatch):
    memory = MemoryManager()
    memory._initialized = True
    memory.embedding_provider = SimpleNamespace(embed_query=lambda text: _embedding())
    captured = {}

    async def store_embedding(vector, payload, point_id=None):
        captured["vector"] = vector
        return "point"

    async def _embedding():
        return [0.25, 0.75]

    monkeypatch.setattr(memory, "store_embedding", store_embedding)
    assert await memory.add_to_knowledge_base("content", {}) == "point"
    assert captured["vector"] == [0.25, 0.75]


@pytest.mark.asyncio
async def test_supervisor_registers_graph_tasks_and_records_agent_metrics(monkeypatch):
    calls = []

    class State:
        async def add_task(self, execution_id, task):
            calls.append(("add", task.task_id))
        async def update_task(self, *args, **kwargs):
            calls.append(("update", args[1]))
        async def update_agent(self, *args, **kwargs):
            return None
        async def record_task_metrics(self, *args):
            calls.append(("metrics", args[1], args[2], args[3]))

    class Agent:
        last_call_metrics = {"tokens": 12, "cost": 0.04}
        async def execute(self, task):
            return {"ok": True}

    supervisor = Supervisor.__new__(Supervisor)
    supervisor.router = SimpleNamespace(get_agent=lambda agent_id: Agent())
    supervisor.agent_logger = SimpleNamespace(log_task_start=lambda *a: None, log_task_complete=lambda *a: None, log_task_error=lambda *a: None)
    supervisor.metrics = SimpleNamespace(metrics=SimpleNamespace(record_retry=lambda: None))
    supervisor.logger = SimpleNamespace(error=lambda *a: None)
    monkeypatch.setattr("multi_agent_system.supervisor.supervisor.state_manager", State())

    graph = TaskGraph()
    graph.add_task(TaskState(task_id="task", agent_id="developer", description="work"))
    await supervisor._execute_task_graph("run", graph)

    assert ("add", "task") in calls
    assert ("metrics", "task", 12, 0.04) in calls


@pytest.mark.asyncio
async def test_supervisor_returns_persisted_execution_metrics(monkeypatch):
    from multi_agent_system.state.models import ExecutionState

    class State:
        def __init__(self):
            self.execution = ExecutionState(execution_id="run", user_request="request")
        async def initialize(self):
            return None
        async def close(self):
            return None
        async def create_execution(self, **kwargs):
            return self.execution
        async def set_final_response(self, execution_id, response, confidence=None):
            self.execution.total_tokens = 27
            self.execution.total_cost = 0.12
            self.execution.completed_tasks = ["task"]
            self.execution.confidence = confidence
        async def get_execution(self, execution_id):
            return self.execution

    class Planner:
        async def create_plan(self, user_request, approach):
            return TaskGraph()

    state = State()
    supervisor = Supervisor.__new__(Supervisor)
    supervisor.logger = SimpleNamespace(info=lambda *a: None, error=lambda *a: None)
    monkeypatch.setattr("multi_agent_system.supervisor.supervisor.state_manager", state)
    monkeypatch.setattr("multi_agent_system.agents.planner.planner.Planner", Planner)
    supervisor._analyze_request = lambda request: _value("general")
    supervisor._execute_task_graph = lambda execution_id, graph: _value({})
    supervisor._aggregate_results = lambda results: _value({"aggregated": "result"})
    supervisor._reflect_and_validate = lambda *args, **kwargs: _value({"confidence": 0.75, "content": "result"})
    supervisor._generate_final_response = lambda *args: _value("answer")

    result = await supervisor.process_request("request")
    assert result["total_tokens"] == 27
    assert result["total_cost"] == 0.12
    assert result["tasks_completed"] == 1
    assert result["confidence"] == 0.75


async def _value(value):
    return value


def test_registered_agents_have_concrete_implementations(monkeypatch):
    monkeypatch.setattr(BaseAgent, "_initialize_llm", lambda self: object())
    router = Router.__new__(Router)
    router.logger = SimpleNamespace(info=lambda *a: None, warning=lambda *a: None)
    for agent_id in (
        "unit_tester", "integration_tester", "data_analyst", "visualizer",
        "docker_agent", "kubernetes_agent", "documentation_writer",
    ):
        assert router.get_agent(agent_id).agent_id == agent_id


def test_reflection_and_qa_parsers_use_model_verdicts():
    assert ReflectionLoop._parse_score('```json\n{"score": 0.95}\n```', 0.0) == 0.95
    assert ReflectionLoop._parse_valid('{"valid": false}') is False

    from multi_agent_system.agents.qa.logic_checker import LogicChecker
    from multi_agent_system.agents.qa.hallucination_detector import HallucinationDetector
    assert LogicChecker._parse_valid('{"valid": false}') is False
    assert HallucinationDetector._parse_clean('{"clean": false}') is False


@pytest.mark.asyncio
async def test_api_quality_flags_are_forwarded(monkeypatch):
    received = {}

    class FakeSupervisor:
        async def process_request(self, **kwargs):
            received.update(kwargs)
            return {
                "execution_id": "id", "response": "ok", "execution_time": 0.0,
                "tasks_completed": 0, "total_cost": 0.0, "total_tokens": 0, "confidence": 1.0,
            }

    monkeypatch.setattr("multi_agent_system.api.routes.Supervisor", FakeSupervisor)
    await execute_request(RequestModel(message="test", enable_reflection=False, enable_qa=False))
    assert received["enable_reflection"] is False
    assert received["enable_qa"] is False
