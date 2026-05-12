"""Result integrator agent - decides loop or proceed"""

import logging
from graph.state import AgentState
from prompts.result_integrator import build_result_integrator_prompt
from ollama import get_llm

logger = logging.getLogger(__name__)


async def result_integrator(state: AgentState) -> AgentState:
    """
    Updates known/missing from latest tool result.
    Decides whether to loop for more tools or proceed.
    """
    
    if not state["tool_results"]:
        state["loop_decision"] = "proceed"
        return state
    
    # Get latest tool result
    latest = state["tool_results"][-1]
    latest_result = latest["result"]
    
    # Build integration prompt
    messages = build_result_integrator_prompt(
        state["known"],
        state["missing"],
        latest_result
    )
    
    # Get LLM decision
    llm = get_llm()
    response = await llm.ainvoke(messages)
    decision = response.content.strip().lower()
    
    # Validate decision
    if decision not in ["loop", "proceed"]:
        logger.warning(f"Invalid decision '{decision}', defaulting to 'proceed'")
        decision = "proceed"
    
    state["loop_decision"] = decision
    state["loop_count"] += 1
    
    logger.debug(f"Integration decision: {decision} (loop_count: {state['loop_count']})")
    
    return state
