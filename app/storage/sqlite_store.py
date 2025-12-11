import json
import sqlite3
from pathlib import Path
from typing import Optional

from models.graph_models import GraphDefinition
from models.run_models import RunRecord

DB_PATH = Path(__file__).resolve().parent / "workflow.db"


def _get_conn():
    # check_same_thread=False allows use across threads in FastAPI/uvicorn
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS graphs (
            id TEXT PRIMARY KEY,
            data TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            graph_id TEXT NOT NULL,
            data TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_graph(graph: GraphDefinition):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO graphs (id, data) VALUES (?, ?)
        """,
        (graph.id, json.dumps(graph.model_dump())),
    )
    conn.commit()
    conn.close()


def get_graph(graph_id: str) -> Optional[GraphDefinition]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM graphs WHERE id = ?", (graph_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = json.loads(row["data"])
    return GraphDefinition.model_validate(data)


def save_run(run: RunRecord):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR REPLACE INTO runs (id, graph_id, data) VALUES (?, ?, ?)
        """,
        (run.id, run.graph_id, json.dumps(run.model_dump())),
    )
    conn.commit()
    conn.close()


def get_run(run_id: str) -> Optional[RunRecord]:
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT data FROM runs WHERE id = ?", (run_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    data = json.loads(row["data"])
    return RunRecord.model_validate(data)
