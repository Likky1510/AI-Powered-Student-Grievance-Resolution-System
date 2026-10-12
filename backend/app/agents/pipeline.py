"""
LangGraph pipeline: wires Classification -> Priority (combined call) ->
Routing into a single graph. This is the "multi-agent orchestration"
layer -- a thin wrapper here, but it's the right place to grow if you
add more steps later (e.g. a draft-response-suggestion node).

State flows through the graph as a TypedDict rather than being re-fetched
from the DB at each node, per the plan.
"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agents.classification_agent import classify_and_prioritize
from app.agents.routing_agent import route_to_department


class GrievanceState(TypedDict):
    grievance_id: str
    raw_text: str
    category: Optional[str]
    category_reason: Optional[str]
    priority: Optional[str]
    priority_reason: Optional[str]
    department_id: Optional[str]
    department_name: Optional[str]


def _classify_node(state: GrievanceState) -> GrievanceState:
    result = classify_and_prioritize(state["raw_text"])
    state["category"] = result["category"]
    state["category_reason"] = result["category_reason"]
    state["priority"] = result["priority"]
    state["priority_reason"] = result["priority_reason"]
    return state


def build_graph(db: Session):
    """
    db is closed over via the routing node since LangGraph state can't
    hold a live SQLAlchemy session cleanly across serialization boundaries
    in more complex setups -- fine for our in-process use here.
    """
    def _route_node(state: GrievanceState) -> GrievanceState:
        department = route_to_department(db, state["category"], state["raw_text"])
        state["department_id"] = department.id
        state["department_name"] = department.name
        return state

    graph = StateGraph(GrievanceState)
    graph.add_node("classify", _classify_node)
    graph.add_node("route", _route_node)

    graph.set_entry_point("classify")
    graph.add_edge("classify", "route")
    graph.add_edge("route", END)

    return graph.compile()


def run_intake_pipeline(db: Session, grievance_id: str, raw_text: str) -> GrievanceState:
    """Entry point used by the grievances router on submission."""
    app_graph = build_graph(db)
    initial_state: GrievanceState = {
        "grievance_id": grievance_id,
        "raw_text": raw_text,
        "category": None,
        "category_reason": None,
        "priority": None,
        "priority_reason": None,
        "department_id": None,
        "department_name": None,
    }
    return app_graph.invoke(initial_state)
