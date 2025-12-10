# engine/registry.py
from typing import Callable, Dict

ToolFunc = Callable[[dict], dict]


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc):
        self._tools[name] = func

    def get(self, name: str) -> ToolFunc:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not found in registry")
        return self._tools[name]

    def all_tools(self):
        return list(self._tools.keys())


# Global registry instance
tool_registry = ToolRegistry()
