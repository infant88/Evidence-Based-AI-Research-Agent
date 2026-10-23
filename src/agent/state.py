"""LangGraph Agent State and Evidence Ledger definitions."""

from typing import TypedDict, List, Dict, Any, Optional

class EvidenceItem(TypedDict):
    source_id: str             # e.g., "doc_chunk_104" or "sql_query_42"
    source_title: str          # e.g., "Q3 Earnings Report (Page 2)"
    quote_or_datapoint: str    # Exact excerpt or aggregate metric
    relevance_rationale: str   # Supporting rationale

class AgentState(TypedDict):
    question: str
    chat_history: List[Dict[str, str]]
    plan_steps: List[str]
    current_step_index: int
    selected_tools: List[str]
    tool_scratchpad: List[Dict[str, Any]]
    retrieved_documents: List[Dict[str, Any]]
    executed_sql: List[Dict[str, Any]]
    python_calculations: List[Dict[str, Any]]
    evidence_ledger: List[EvidenceItem]
    verification_attempts: int
    is_evidence_sufficient: bool
    requires_human_approval: bool
    approval_prompt: Optional[str]
    final_report: Optional[str]
    groundedness_score: float
    citation_score: float
    latency_breakdown: Dict[str, float]
    metadata: Dict[str, Any]
