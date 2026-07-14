# Agents

Agents inherit `BaseAgent`, own their tools, and implement `get_system_prompt` and async `execute`. The router maps task IDs to configured specialised agents. The supervisor coordinates agents; it does not perform domain work itself.

The research retriever receives an injected `RAGPipeline` (or builds the default one). Other agents can use the same interface without depending on the retriever agent.
