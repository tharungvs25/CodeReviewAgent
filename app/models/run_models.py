# models/run_models.py
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
import uuid


class RunStatus(str):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RunRecord(BaseModel):
    id: str
    graph_id: str
    state: Dict[str, object] = Field(default_factory=dict)
    log: List[str] = Field(default_factory=list)
    current_node: Optional[str] = None
    status: str = RunStatus.PENDING
    error: Optional[str] = None


def new_run_id() -> str:
    return str(uuid.uuid4())
