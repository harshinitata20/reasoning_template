"""Graph builder for the domain-agnostic analysis pipeline."""

import logging

from langgraph.graph import END, START, StateGraph

from agents.materiality_filter import materiality_filter
from agents.output_writer import output_writer
from agents.result_integrator import result_integrator
from agents.router import router
from agents.second_order import second_order_reasoning
from agents.think_phase import think_phase
from agents.tool_executor import tool_executor
from agents.tool_selector import tool_selector
from graph.edges import loop_or_proceed
from graph.state import AgentState

logger = logging.getLogger(__name__)


def build_graph():
    """Assemble the complete StateGraph."""

    workflow = StateGraph(AgentState)

    workflow.add_node("router", router)
    workflow.add_node("think_phase", think_phase)
    workflow.add_node("tool_selector", tool_selector)
    workflow.add_node("tool_executor", tool_executor)
    workflow.add_node("result_integrator", result_integrator)
    workflow.add_node("materiality_filter", materiality_filter)
    workflow.add_node("second_order", second_order_reasoning)
    workflow.add_node("output_writer", output_writer)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "think_phase")
    workflow.add_edge("think_phase", "tool_selector")
    workflow.add_edge("tool_selector", "tool_executor")
    workflow.add_edge("tool_executor", "result_integrator")
    workflow.add_conditional_edges(
        "result_integrator",
        loop_or_proceed,
        {
            "tool_selector": "tool_selector",
            "materiality": "materiality_filter",
        },
    )
    workflow.add_edge("materiality_filter", "second_order")
    workflow.add_edge("second_order", "output_writer")
    workflow.add_edge("output_writer", END)

    logger.info("Graph compiled without external observability layer")
    return workflow.compile()
