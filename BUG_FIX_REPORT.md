# Bug Fix Report

## Supervisor metrics

- **Issue:** Execution responses reported zero task usage because the supervisor never persisted task duration, token use, or cost.
- **Root cause:** Agent call metrics were recorded globally but were not copied to the execution state, and the supervisor returned its stale in-memory execution object.
- **Fix:** Agents retain the usage from their most recent LLM call; the supervisor records it per task, the state manager recalculates execution totals atomically, and the final response reloads the persisted execution metrics and confidence.
- **Test added:** `test_supervisor_registers_graph_tasks_and_records_agent_metrics`, `test_supervisor_returns_persisted_execution_metrics`, and `test_state_mutations_are_serialized_and_task_metrics_are_persisted`.

## Shared singleton lifecycle

- **Issue:** A request could close the shared state or memory manager while the API lifespan or another request was still using it.
- **Root cause:** Global managers had no ownership accounting; every `close()` disposed the shared connections.
- **Fix:** Both managers now use a lifecycle lock and lease counter. Connections are disposed only after the final matching close.
- **Test added:** `test_shared_state_manager_does_not_close_until_final_lease`.

## Missing agent implementations

- **Issue:** Seven agents in the registry mapped to missing modules. The router then attempted to instantiate abstract `BaseAgent`, causing runtime failures.
- **Root cause:** Registry and router mappings were added before concrete implementations existed.
- **Fix:** Added concrete configured implementations for testing, analytics, deployment, and documentation agents; updated packaging so those modules ship with the application. The router now raises a clear runtime error for a genuinely unavailable implementation instead of creating an abstract class.
- **Test added:** `test_registered_agents_have_concrete_implementations`.

## Reflection parsing

- **Issue:** Reflection and QA results used hard-coded scores and verdicts, regardless of model output.
- **Root cause:** Parsing was left as placeholder comments.
- **Fix:** Added bounded JSON and text parsing for score, confidence, validity, and cleanliness. Missing or malformed verdicts fail conservatively.
- **Test added:** `test_reflection_and_qa_parsers_use_model_verdicts`.

## API flags

- **Issue:** `enable_reflection` and `enable_qa` were accepted by `/execute` but ignored.
- **Root cause:** The route did not pass either flag to the supervisor.
- **Fix:** Forwarded both flags and made supervisor validation conditionally run reflection and QA while preserving default behavior.
- **Test added:** `test_api_quality_flags_are_forwarded`.

## State race conditions

- **Issue:** Parallel task and agent updates could overwrite each other; additionally, planned tasks were not registered in execution state, making updates no-ops.
- **Root cause:** Read-modify-write operations had no per-execution synchronization, and graph state was separate from persisted execution state.
- **Fix:** Added per-execution mutation locks and register all graph tasks before execution. Progress now treats terminal failures as completed work.
- **Test added:** `test_state_mutations_are_serialized_and_task_metrics_are_persisted` and `test_supervisor_registers_graph_tasks_and_records_agent_metrics`.

## Placeholder persistence

- **Issue:** State execution persistence and long-term/user memory persistence were no-op placeholders.
- **Root cause:** PostgreSQL tables and CRUD operations had not been implemented.
- **Fix:** Added schema initialization and JSON-backed upsert/retrieval paths for execution state, long-term memory, and user preferences. Redis cache misses now restore execution state from PostgreSQL. Knowledge-base writes now generate a real embedding instead of storing an all-zero placeholder vector.
- **Test added:** `test_postgres_persistence_paths_write_execution_and_memory_records` and `test_knowledge_base_uses_a_real_embedding_when_none_is_supplied`.
