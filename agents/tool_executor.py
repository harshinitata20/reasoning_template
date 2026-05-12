"""Tool executor agent - executes selected tool."""

import logging

from graph.state import AgentState
from tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


async def tool_executor(state: AgentState) -> AgentState:
    """Execute the selected tool and append its plain-text result."""

    if not state["selected_tool"]:
        logger.warning("No tool selected, skipping execution")
        return state

    tool_name = state["selected_tool"]
    tool = ToolRegistry.get_tool(state["domain"], tool_name)
    if not tool:
        logger.error(f"Tool '{tool_name}' not found in registry")
        return state

    try:
        result = tool.run(query=state["query"], context=state["context"])
        cached_flag = False
        logger.info(f"Tool '{tool_name}' executed successfully")
    except Exception as e:
        logger.error(f"Tool execution failed: {e}")
        result = f"Error executing {tool_name}: {str(e)}"
        cached_flag = False

    state["tool_results"].append(
        {
            "tool_name": tool_name,
            "result": result,
            "cached": cached_flag,
        }
    )

    return state
