# API

Interactive OpenAPI documentation is available at `/api/docs`.

`POST /api/v1/execute` accepts a message and optional conversation ID. `GET /api/v1/execution/{execution_id}` returns progress. Agent, task, conversation, memory statistics, health, and Prometheus metrics endpoints are also available.

Example:

```bash
curl -X POST localhost:8000/api/v1/execute -H 'content-type: application/json' \
  -d '{"message":"Summarize the indexed architecture documentation"}'
```
