"""Materiality filter agent - scores and filters findings"""

import logging
from graph.state import AgentState
from prompts.materiality_filter import build_materiality_filter_prompt
from llm import get_llm
from config.settings import settings
import json

logger = logging.getLogger(__name__)


async def materiality_filter(state: AgentState) -> AgentState:
    """
    Scores findings 1-5 by business impact.
    Filters below threshold.
    """
    
    if not state["tool_results"]:
        logger.warning("No tool results to filter")
        return state
    
    # Combine all tool results into findings text
    findings_text = "\n".join([
        f"{i}. {result['tool_name']}: {result['result']}"
        for i, result in enumerate(state["tool_results"], 1)
    ])
    
    # Build materiality prompt
    messages = build_materiality_filter_prompt(
        findings_text,
        settings.MATERIALITY_THRESHOLD
    )
    
    # Get LLM scoring
    llm = get_llm()
    response = await llm.ainvoke(messages)
    
    # Parse scored findings
    try:
        scored_findings = json.loads(response.content)
        if not isinstance(scored_findings, list):
            scored_findings = [scored_findings]
    except json.JSONDecodeError:
        logger.warning("Failed to parse LLM response, using all results")
        scored_findings = [
            {"text": r["result"], "score": 3, "category": "finding"}
            for r in state["tool_results"]
        ]
    
    # Filter by threshold
    state["findings"] = [
        f for f in scored_findings
        if f.get("score", 0) >= settings.MATERIALITY_THRESHOLD
    ]
    
    logger.info(f"Materiality filter: {len(state['findings'])} material findings")
    
    return state
