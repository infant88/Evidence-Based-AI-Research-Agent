"""Master Runner: Runs the 60-question evaluation benchmark suite and launches the Web UI."""

import sys
import socket
import webbrowser
import time
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.run_benchmark import run_evaluation

def is_port_in_use(port: int = 8000, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def find_available_port(start_port: int = 8000) -> int:
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def main():
    print("=" * 70)
    print("   EVIDENCE-BASED AI RESEARCH AGENT: FULL TEST & UI LAUNCHER")
    print("=" * 70)
    
    # 1. Run the 60-Question Empirical Evaluation Benchmark
    print("\n[STEP 1/2] Running Complete Empirical Evaluation Suite (60 Questions)...")
    summary = run_evaluation(sample_limit=60)
    
    print("\n" + "=" * 70)
    print("   BENCHMARK EVALUATION RESULTS")
    print("=" * 70)
    print(f" • Retrieval Recall@5        : {summary['mean_recall_at_5'] * 100:.1f}% (Target: >= 85.0%)")
    print(f" • Retrieval MRR             : {summary['mean_mrr']:.3f} (Target: >= 0.750)")
    print(f" • Tool Selection F1         : {summary['mean_tool_f1'] * 100:.1f}% (Target: >= 90.0%)")
    print(f" • SQL Execution Validity    : {summary['sql_execution_success_rate'] * 100:.1f}% (Target: >= 95.0%)")
    print(f" • Groundedness / Faithfulness: {summary['mean_groundedness'] * 100:.1f}% (Target: >= 90.0%)")
    print(f" • Citation Accuracy         : {summary['mean_citation_accuracy'] * 100:.1f}% (Target: >= 90.0%)")
    print(f" • Latency (P50 / P90)       : {summary['latency_p50_seconds']}s / {summary['latency_p90_seconds']}s")
    print(f" • Total Evaluated Questions : {summary['total_samples']}")
    print("=" * 70)

    # 2. Launch FastAPI Web UI
    print("\n[STEP 2/2] Checking Interactive Research Dashboard Server...")
    target_port = 8000

    if is_port_in_use(target_port):
        print(f"Server is already active and serving at: http://127.0.0.1:{target_port}")
        print("Opening browser...")
        webbrowser.open(f"http://127.0.0.1:{target_port}")
        print("\nAll tests completed and UI is live at http://127.0.0.1:8000! Enjoy exploring.")
        return

    print(f"Starting server on http://127.0.0.1:{target_port}...")
    try:
        webbrowser.open(f"http://127.0.0.1:{target_port}")
    except Exception:
        pass

    import uvicorn
    from src.web.server import app
    uvicorn.run(app, host="127.0.0.1", port=target_port)

if __name__ == "__main__":
    main()
