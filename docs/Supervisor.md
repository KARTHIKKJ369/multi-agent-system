# Supervisor

`Supervisor.process_request` creates an execution ID, asks the planner for a dependency graph, runs ready tasks concurrently, retries failed tasks with exponential backoff, aggregates results, then performs QA/reflection before returning a response.

Execution state is updated through `StateManager`; avoid mutating task state directly from agents.
