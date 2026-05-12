"""Shared state for the generic analysis pipeline."""

from typing import Any, Optional, TypedDict


class AgentState(TypedDict):
    query: str
    context: dict[str, Any]
    run_id: str
    domain: str
    known: dict[str, Any]
    assumptions: list[str]
    missing: list[str]
    available_tools: list[str]
    selected_tool: Optional[str]
    tool_results: list[dict[str, Any]]
    loop_decision: Optional[str]
    loop_count: int
    findings: list[dict[str, Any]]
    second_order_risks: list[dict[str, Any]]
    reasoning: str
    output_path: Optional[str]