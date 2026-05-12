"""Conditional edge logic for the pipeline graph"""

from graph.state import AgentState
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


def loop_or_proceed(state: AgentState) -> str:
    """
    Conditional edge: should we loop back for more tools or proceed to filtering?
    
    Returns:
        "tool_selector" to loop, "materiality" to proceed
    """
    
    # Check max iterations guard
    if state["loop_count"] >= settings.MAX_LOOP_ITERATIONS:
        logger.warning(f"Max loop iterations ({settings.MAX_LOOP_ITERATIONS}) reached")
        return "materiality"
    
    # Check integrator's decision
    decision = state.get("loop_decision", "proceed")
    
    if decision == "loop":
        logger.debug(f"Looping (iteration {state['loop_count'] + 1})")
        return "tool_selector"
    else:
        logger.debug("Proceeding to materiality filtering")
        return "materiality"
