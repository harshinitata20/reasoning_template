"""Tool selector agent - selects which tool to execute"""

import logging
from graph.state import AgentState
from prompts.tool_selector import build_tool_selector_prompt
from ollama import get_llm
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


async def tool_selector(state: AgentState) -> AgentState:
    """
    Selects the best tool for the current missing information.
    Completely generic - uses registry to get domain-specific tools.
    """
    
    # Get tools available for this domain
    tools = ToolRegistry.get_tool_names(state["domain"])
    state["available_tools"] = tools
    
    if not tools:
        logger.warning(f"No tools available for domain '{state['domain']}'")
        state["selected_tool"] = None
        return state
    
    # Build tool selection prompt
    messages = build_tool_selector_prompt(
        tools,
        state["missing"],
        state["query"]
    )
    
    # Get LLM response
    llm = get_llm()
    response = await llm.ainvoke(messages)
    selected = response.content.strip().lower()
    
    # Validate tool exists
    if selected not in tools:
        logger.warning(f"Tool '{selected}' not in available tools, using first available")
        selected = tools[0] if tools else None
    
    state["selected_tool"] = selected
    logger.debug(f"Selected tool: {selected}")
    
    return state
