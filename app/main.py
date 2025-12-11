# main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
from models.graph_models import (
    GraphCreateRequest,
    GraphCreateResponse,
    GraphRunRequest,
    GraphRunResponse,
    GraphDefinition,
)
from models.run_models import RunRecord
from storage.sqlite_store import init_db, save_graph, get_graph, get_run
from engine.runner import run_graph
from workflows.code_review import register_code_review_tools, create_code_review_graph

app = FastAPI(title="Minimal Workflow / Graph Engine")


@app.on_event("startup")
def startup_event():
    from workflows.code_review import register_code_review_tools, create_code_review_graph

    init_db()

    # Register tools
    register_code_review_tools()

    # Create the graph with ID = "code_review" and persist it
    graph = create_code_review_graph()
    save_graph(graph)

    print("Loaded graph:", graph.id)


# --- Graph Endpoints ---

@app.post("/graph/create", response_model=GraphCreateResponse)
def create_graph(req: GraphCreateRequest):
    graph = GraphDefinition(
        id=req.start_node,  # simple id choice, or use a UUID if you prefer
        nodes=req.nodes,
        edges=req.edges,
        start_node=req.start_node,
    )

    if get_graph(graph.id):
        raise HTTPException(status_code=400, detail="Graph with this id already exists")

    save_graph(graph)
    return GraphCreateResponse(graph_id=graph.id)


@app.post("/graph/run", response_model=GraphRunResponse)
def run_graph_endpoint(req: GraphRunRequest):
    graph = get_graph(req.graph_id)
    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    run, final_state, log = run_graph(graph, req.initial_state)
    return GraphRunResponse(run_id=run.id, final_state=final_state, log=log)


@app.get("/graph/state/{run_id}", response_model=RunRecord)
def get_run_state(run_id: str):
    run = get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

@app.get("/", response_class=HTMLResponse)
def ui_home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Code Review Mini-Agent</title>
    <style>
        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            margin: 0;
            padding: 1.5rem;
            background: #0f172a;
            color: #e5e7eb;
        }
        h1 {
            margin-bottom: 0.5rem;
        }
        .subtitle {
            color: #9ca3af;
            margin-bottom: 1.5rem;
        }
        .container {
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 1.5rem;
        }
        .card {
            background: #020617;
            border-radius: 0.75rem;
            padding: 1rem 1.25rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            border: 1px solid #1f2937;
        }
        textarea, input {
            width: 100%;
            box-sizing: border-box;
            border-radius: 0.5rem;
            border: 1px solid #374151;
            background: #020617;
            color: #e5e7eb;
            padding: 0.5rem 0.75rem;
            font-family: monospace;
            resize: vertical;
        }
        label {
            display: block;
            margin-top: 0.75rem;
            margin-bottom: 0.25rem;
            font-size: 0.9rem;
            color: #9ca3af;
        }
        button {
            margin-top: 0.75rem;
            padding: 0.6rem 1.2rem;
            border-radius: 9999px;
            border: none;
            cursor: pointer;
            font-weight: 600;
            background: linear-gradient(to right, #4f46e5, #22d3ee);
            color: white;
        }
        button:disabled {
            opacity: 0.6;
            cursor: default;
        }
        .steps ol {
            padding-left: 1.25rem;
            font-size: 0.9rem;
        }
        .steps li {
            margin-bottom: 0.15rem;
        }
        .badge-loop {
            display: inline-block;
            padding: 0.15rem 0.6rem;
            border-radius: 999px;
            font-size: 0.7rem;
            background: #22c55e33;
            color: #bbf7d0;
            margin-left: 0.4rem;
        }
        .section-title {
            font-size: 0.95rem;
            font-weight: 600;
            margin-top: 0.5rem;
            margin-bottom: 0.25rem;
        }
        pre {
            background: #020617;
            border-radius: 0.5rem;
            padding: 0.5rem 0.75rem;
            font-size: 0.78rem;
            overflow-x: auto;
            border: 1px solid #1f2937;
        }
        .tag {
            display: inline-block;
            font-size: 0.75rem;
            padding: 0.1rem 0.5rem;
            border-radius: 999px;
            background: #111827;
            border: 1px solid #1f2937;
            margin: 0.1rem;
        }
        .score-ok {
            color: #22c55e;
        }
        .score-bad {
            color: #f97316;
        }
        .log {
            max-height: 160px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <h1>Code Review Mini-Agent</h1>
    <div class="subtitle">Option A · Minimal Workflow Engine · Nodes + State + Looping</div>

    <div class="container">
        <!-- Left: Input -->
        <div class="card">
            <div class="steps">
                <div class="section-title">Workflow</div>
                <ol>
                    <li>Extract functions</li>
                    <li>Check complexity</li>
                    <li>Detect basic issues</li>
                    <li>Suggest improvements</li>
                    <li>Loop until <code>quality_score &gt;= threshold</code><span class="badge-loop">loop node</span></li>
                </ol>
            </div>

            <label for="code">Code to review</label>
            <textarea id="code" rows="14" placeholder="Paste your Python code here..."></textarea>

            <label for="threshold">Quality threshold (0–1)</label>
            <input id="threshold" type="number" step="0.05" min="0" max="1" value="0.8" />

            <button id="runBtn">Run Review</button>
            <div id="status" class="subtitle" style="margin-top:0.5rem;"></div>
        </div>

        <!-- Right: Results -->
        <div class="card">
            <div class="section-title">Result</div>
            <div id="result-score"></div>

            <div class="section-title">Functions</div>
            <div id="result-functions"><span class="subtitle">No run yet.</span></div>

            <div class="section-title">Complexity</div>
            <pre id="result-complexity">// waiting...</pre>

            <div class="section-title">Issues</div>
            <pre id="result-issues">// waiting...</pre>

            <div class="section-title">Suggestions</div>
            <div id="result-suggestions"><span class="subtitle">None yet.</span></div>

            <div class="section-title">Execution log</div>
            <pre id="result-log" class="log">// waiting...</pre>
        </div>
    </div>

    <script>
        const runBtn = document.getElementById("runBtn");
        const statusEl = document.getElementById("status");

        const codeEl = document.getElementById("code");
        const thresholdEl = document.getElementById("threshold");

        const scoreEl = document.getElementById("result-score");
        const functionsEl = document.getElementById("result-functions");
        const complexityEl = document.getElementById("result-complexity");
        const issuesEl = document.getElementById("result-issues");
        const suggestionsEl = document.getElementById("result-suggestions");
        const logEl = document.getElementById("result-log");

        runBtn.addEventListener("click", async () => {
            const code = codeEl.value.trim();
            const threshold = parseFloat(thresholdEl.value || "0.8");

            if (!code) {
                statusEl.textContent = "Please paste some code.";
                return;
            }

            runBtn.disabled = true;
            statusEl.textContent = "Running workflow...";
            scoreEl.innerHTML = "";
            logEl.textContent = "// running...";

            try {
                const payload = {
                    graph_id: "code_review",
                    initial_state: {
                        code: code,
                        threshold: threshold
                    }
                };

                const res = await fetch("/graph/run", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(payload)
                });

                if (!res.ok) {
                    const errorText = await res.text();
                    statusEl.textContent = "Error: " + errorText;
                    runBtn.disabled = false;
                    return;
                }

                const data = await res.json();
                statusEl.textContent = "Run ID: " + data.run_id;

                const st = data.final_state || {};

                const q = typeof st.quality_score === "number" ? st.quality_score : null;
                const cls = q !== null && q >= threshold ? "score-ok" : "score-bad";
                scoreEl.innerHTML = q === null
                    ? "<span class='subtitle'>quality_score not set.</span>"
                    : `<div>quality_score: <span class="${cls}">${q}</span> (threshold: ${threshold})</div>`;

                const funcs = st.functions || [];
                if (funcs.length === 0) {
                    functionsEl.innerHTML = "<span class='subtitle'>No functions detected.</span>";
                } else {
                    functionsEl.innerHTML = funcs.map(f => `<span class="tag">${f}</span>`).join(" ");
                }

                complexityEl.textContent = JSON.stringify(st.complexity || {}, null, 2);
                issuesEl.textContent = JSON.stringify(st.issues || {}, null, 2);

                const sug = (st.suggestions && st.suggestions.suggestions) || [];
                if (sug.length === 0) {
                    suggestionsEl.innerHTML = "<span class='subtitle'>No suggestions.</span>";
                } else {
                    suggestionsEl.innerHTML = sug.map(s => `<div>• ${s}</div>`).join("");
                }

                logEl.textContent = (data.log || []).join("\\n");
            } catch (e) {
                statusEl.textContent = "Error: " + e;
            } finally {
                runBtn.disabled = false;
            }
        });
    </script>
</body>
</html>
    """
