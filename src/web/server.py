"""FastAPI Application Server for Evidence-Based AI Research Agent."""

import time
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config.config import settings
from src.agent.graph import run_agent_query
from src.tools.sql_sandbox import SQLSandbox
from src.tools.rag_tool import RAGTool
from evaluation.run_benchmark import run_evaluation, REPORT_PATH

app = FastAPI(
    title="Evidence-Based AI Research Agent",
    description="Agentic Research Engine with LangGraph, Hybrid RAG, Sandboxed SQL, and Benchmark Metrics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    provider: Optional[str] = "mock"

class BenchmarkRequest(BaseModel):
    sample_limit: Optional[int] = 60

sql_sandbox = SQLSandbox()
rag_tool = RAGTool()

@app.post("/api/query")
def query_endpoint(req: QueryRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    t0 = time.time()
    result = run_agent_query(req.question)
    elapsed = round(time.time() - t0, 3)
    
    return {
        "question": req.question,
        "elapsed_seconds": elapsed,
        "final_report": result.get("final_report"),
        "groundedness_score": result.get("groundedness_score"),
        "citation_score": result.get("citation_score"),
        "is_evidence_sufficient": result.get("is_evidence_sufficient"),
        "evidence_ledger": result.get("evidence_ledger", []),
        "executed_sql": result.get("executed_sql", []),
        "retrieved_documents": result.get("retrieved_documents", []),
        "python_calculations": result.get("python_calculations", []),
        "plan_steps": result.get("plan_steps", []),
        "tool_scratchpad": result.get("tool_scratchpad", [])
    }

@app.post("/api/benchmark/run")
def run_benchmark_endpoint(req: BenchmarkRequest):
    limit = req.sample_limit or 60
    summary = run_evaluation(sample_limit=limit)
    return summary

@app.get("/api/benchmark/latest")
def get_latest_benchmark():
    if REPORT_PATH.exists():
        content = REPORT_PATH.read_text(encoding="utf-8")
        return {"report_markdown": content, "exists": True}
    return {"report_markdown": "No benchmark report generated yet. Run the evaluation suite.", "exists": False}

@app.get("/api/database/schema")
def get_db_schema():
    summary = sql_sandbox.get_schema_summary()
    return {"schema_summary": summary, "allowed_tables": settings.SQL_ALLOWED_TABLES}

@app.get("/api/documents")
def get_documents_list():
    docs = []
    for f in settings.DOCS_DIR.glob("*.*"):
        docs.append({
            "name": f.name,
            "size_kb": round(f.stat().st_size / 1024, 2),
            "type": f.suffix.replace(".", "").upper()
        })
    return {"documents": docs, "total_chunks": len(rag_tool.retriever.chunks)}

# Mount static frontend files
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
