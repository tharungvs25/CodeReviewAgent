# engine/graph.py
from typing import Optional
from models.graph_models import GraphDefinition
from engine.registry import tool_registry


class GraphEngine:
    """
    Minimal graph engine:
    - Each node maps to a tool (function) in the registry.
    - Edges define default next node.
    - Nodes can override next node by setting '_next_node' in state.
    """

    def __init__(self, graph: GraphDefinition):
        self.graph = graph

    def get_start_node(self) -> str:
        return self.graph.start_node

    def get_tool_for_node(self, node_name: str):
        node_cfg = self.graph.nodes[node_name]
        return tool_registry.get(node_cfg.tool_name)

    def get_default_next_node(self, node_name: str) -> Optional[str]:
        return self.graph.edges.get(node_name)
