# storage/memory.py
from typing import Dict
from models.graph_models import GraphDefinition
from models.run_models import RunRecord

# In-memory stores (for assignment this is enough)
GRAPHS: Dict[str, GraphDefinition] = {}
RUNS: Dict[str, RunRecord] = {}
