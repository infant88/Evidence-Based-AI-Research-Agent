"""Router and Planning node for orchestrating heterogeneous tools."""

from typing import Dict, Any
from config.prompts import ROUTER_PLANNER_PROMPT
from src.providers.llm_factory import get_llm_client
from src.agent.state import AgentState

def plan_and_route(state: AgentState) -> Dict[str, Any]:
    """Analyzes the question and produces an actionable plan with selected tools."""
    llm = get_llm_client()
    question = state["question"]
    
    prompt = f"Decompose this research question and select tools:\nQuestion: '{question}'"
    routing_decision = llm.generate_json(prompt, system_prompt=ROUTER_PLANNER_PROMPT)
    
    tools = routing_decision.get("required_tools", ["execute_sql", "execute_rag"])
    sub_questions = routing_decision.get("sub_questions", [])

    return {
        "plan_steps": sub_questions,
        "selected_tools": tools,
        "current_step_index": 0,
        "tool_scratchpad": state.get("tool_scratchpad", []) + [{
            "step": "plan_and_route",
            "decision": routing_decision
        }]
    }
