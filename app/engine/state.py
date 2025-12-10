# engine/state.py
from typing import Any, Dict
from pydantic import BaseModel, Field


class WorkflowState(BaseModel):
    """Shared state passed between nodes."""
    data: Dict[str, Any] = Field(default_factory=dict)

    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value
