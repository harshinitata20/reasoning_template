"""Think phase agent - structured reasoning"""

import logging
from graph.state import AgentState
from prompts.think_phase import build_think_phase_prompt
from llm import get_llm
import re

logger = logging.getLogger(__name__)


async def think_phase(state: AgentState) -> AgentState:
    """
    Generic structured reasoning pass.
    Populates: known, assumptions, missing
    """
    
    # Build think phase prompt
    messages = build_think_phase_prompt(state["query"], state["context"])
    
    # Get LLM response
    llm = get_llm()
    response = await llm.ainvoke(messages)
    content = response.content
    
    # Parse XML sections
    known_match = re.search(r'<known>(.*?)</known>', content, re.DOTALL)
    assumptions_match = re.search(r'<assumptions>(.*?)</assumptions>', content, re.DOTALL)
    missing_match = re.search(r'<missing>(.*?)</missing>', content, re.DOTALL)
    
    # Extract and clean content
    known_text = known_match.group(1).strip() if known_match else ""
    assumptions_text = assumptions_match.group(1).strip() if assumptions_match else ""
    missing_text = missing_match.group(1).strip() if missing_match else ""
    
    # Parse into structured format
    state["known"] = {"facts": known_text}
    state["assumptions"] = [a.strip() for a in assumptions_text.split("\n") if a.strip()]
    state["missing"] = [m.strip() for m in missing_text.split("\n") if m.strip()]
    
    logger.debug(f"Think phase: {len(state['missing'])} missing fields")
    
    return state
