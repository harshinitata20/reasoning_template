"""Second-order reasoning agent - causal chains and risks"""

import logging
from graph.state import AgentState
from prompts.second_order import build_second_order_prompt
from llm import get_llm
import json

logger = logging.getLogger(__name__)


async def second_order_reasoning(state: AgentState) -> AgentState:
    """
    Extracts second-order risks and causal chains from findings.
    """
    
    if not state["findings"]:
        logger.info("No findings to analyze for second-order risks")
        return state
    
    # Format findings for analysis
    findings_text = "\n".join([
        f"- {f.get('text', '')} (score: {f.get('score', 0)})"
        for f in state["findings"]
    ])
    
    # Build second-order prompt
    messages = build_second_order_prompt(findings_text)
    
    # Get LLM analysis
    llm = get_llm()
    response = await llm.ainvoke(messages)
    
    # Parse risks (simple parsing, could be more sophisticated)
    try:
        risks = json.loads(response.content)
        if not isinstance(risks, list):
            risks = [risks]
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM risk response")
        risks = []
    
    state["second_order_risks"] = risks
    state["reasoning"] = response.content
    
    logger.info(f"Second-order analysis: {len(risks)} risks identified")
    
    return state
