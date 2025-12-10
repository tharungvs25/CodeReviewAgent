# models/graph_models.py
from typing import Dict, Optional
from pydantic import BaseModel, Field
import uuid


class GraphNodeConfig(BaseModel):
    """Maps a logical node name to a tool/function in the registry."""
    tool_name: str = Field(..., description="Name of the tool in the registry")


class GraphDefinition(BaseModel):
    id: str
    nodes: Dict[str, GraphNodeConfig]
    edges: Dict[str, Optional[str]]
    start_node: str


class GraphCreateRequest(BaseModel):
    nodes: Dict[str, GraphNodeConfig]
    edges: Dict[str, Optional[str]]
    start_node: str


class GraphCreateResponse(BaseModel):
    graph_id: str


class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, object]


class GraphRunResponse(BaseModel):
    run_id: str
    final_state: Dict[str, object]
    log: list


def new_graph_id() -> str:
    return str(uuid.uuid4())
