# engine/runner.py
from typing import Dict, Any, Tuple
from models.graph_models import GraphDefinition
from models.run_models import RunRecord, RunStatus, new_run_id
from storage.sqlite_store import save_run
from engine.graph import GraphEngine


MAX_STEPS = 100  # safety guard


def run_graph(graph: GraphDefinition, initial_state: Dict[str, Any]) -> Tuple[RunRecord, Dict[str, Any], list]:
    run_id = new_run_id()
    engine = GraphEngine(graph)

    run = RunRecord(
        id=run_id,
        graph_id=graph.id,
        state=initial_state.copy(),
        current_node=engine.get_start_node(),
        status=RunStatus.RUNNING,
        log=[]
    )
    save_run(run)

    steps = 0

    try:
        while run.current_node is not None and steps < MAX_STEPS:
            steps += 1
            node_name = run.current_node
            tool = engine.get_tool_for_node(node_name)

            run.log.append(f"Running node: {node_name}")
            # Call node function
            new_state = tool(run.state) or run.state
            run.state = new_state

            # Branching / looping: node can set '_next_node'
            override_next = run.state.pop("_next_node", None)
            if override_next:
                run.log.append(f"Next node overridden by state to: {override_next}")
                run.current_node = override_next
            else:
                next_node = engine.get_default_next_node(node_name)
                run.current_node = next_node
                if next_node:
                    run.log.append(f"Next node (default edge): {next_node}")
                else:
                    run.log.append("No next node, workflow completed")

        if steps >= MAX_STEPS:
            run.status = RunStatus.FAILED
            run.error = "Max steps exceeded (possible infinite loop)"
        else:
            run.status = RunStatus.COMPLETED

    except Exception as exc:
        run.status = RunStatus.FAILED
        run.error = str(exc)
        run.log.append(f"Error: {exc}")

    save_run(run)
    return run, run.state, run.log
