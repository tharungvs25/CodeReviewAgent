# CodeReviewAgent – Minimal Workflow / Graph Engine

A small FastAPI app that runs configurable workflow graphs. Each node is a Python function that reads/modifies shared state; edges define execution order; nodes can branch/loop by setting `_next_node` in state. A default `code_review` workflow is preloaded with looping support and persisted in SQLite.

## Features
- Nodes as plain Python functions registered in a tool registry
- Shared state dict flows between nodes; nodes can override next hop via `_next_node`
- Branching and looping with safety guards (`MAX_STEPS` + loop counter)
- SQLite persistence for graphs and runs (`app/storage/workflow.db`)
- FastAPI endpoints plus Swagger UI at `/docs`
- Default code review workflow: extraction, complexity check, issue detection, suggestions, quality scoring (with loop)

## Quickstart
```bash
cd app
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
uvicorn main:app --reload
```
App runs at http://127.0.0.1:8000 (hot reload). Swagger UI: http://127.0.0.1:8000/docs

## API
### POST /graph/create
Create a graph.
```json
{
  "nodes": {"extract": {"tool_name": "extract_functions"}},
  "edges": {"extract": null},
  "start_node": "extract"
}
```
Response: `{ "graph_id": "extract" }`

### POST /graph/run
Run a graph with initial state.
```json
{
  "graph_id": "code_review",
  "initial_state": {
    "code": "def foo():\n    return 1",
    "threshold": 0.8
  }
}
```
Response includes `run_id`, `final_state`, and `log`.

### GET /graph/state/{run_id}
Fetch the stored `RunRecord` for a prior run.

## Default Workflow (code_review)
Order: `extract_functions` → `check_complexity` → `detect_issues` → `suggest_improvements` → `check_quality`.
`check_quality` loops back to `suggestions` until `quality_score >= threshold` or max loops reached.

State fields: `functions`, `complexity`, `issues`, `suggestions`, `quality_score`, `_loop_count`, `_loop_message`.

## Storage
- SQLite DB at `app/storage/workflow.db`
- Helpers in `storage/sqlite_store.py`: `init_db`, `save_graph`, `get_graph`, `save_run`, `get_run`

## Project Structure
```
app/
├── main.py              # FastAPI app & endpoints
├── requirements.txt     # Dependencies
├── engine/
│   ├── graph.py        # GraphEngine (maps nodes to tools)
│   ├── registry.py     # ToolRegistry (tool lookup)
│   ├── runner.py       # Graph execution loop
│   └── state.py        # WorkflowState model
├── models/
│   ├── graph_models.py # GraphDefinition, GraphNodeConfig
│   └── run_models.py   # RunRecord, RunStatus
├── workflows/
│   └── code_review.py  # Default code review workflow
└── storage/
    ├── memory.py       # In-memory stores (deprecated)
    └── sqlite_store.py # SQLite persistence layer
```

## Example: Running Code Review
```python
import requests

api = "http://127.0.0.1:8000/graph/run"
payload = {
    "graph_id": "code_review",
    "initial_state": {
        "code": "def add(a, b):\n    return a + b",
        "threshold": 0.8
    }
}
resp = requests.post(api, json=payload)
data = resp.json()
print(f"Run ID: {data['run_id']}")
print(f"Quality: {data['final_state']['quality_score']}")
print(f"Suggestions: {data['final_state']['suggestions']}")
```

## Notes
- Default graph id: `code_review`
- MAX_STEPS=100 guard prevents infinite loops
- Loop counter caps iterations to max 3 to avoid runaway loops
- All graphs and runs persist to SQLite on save
