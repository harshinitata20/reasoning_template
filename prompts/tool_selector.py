"""Prompt builder for tool_selector agent"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_tool_selector_prompt(
    available_tools: List[str],
    missing_fields: List[str],
    query: str,
) -> List[BaseMessage]:
    """
    Build tool selection prompt.
    
    Injects the list of tools available for the current domain.
    Agent picks the single best tool to execute next.
    
    Completely generic — domain tools were already filtered by the registry.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = """You are a tool selector. Given a query and available tools, select the single most appropriate tool to execute next.

Respond with ONLY the tool name in lowercase, nothing else."""
    
    tools_str = "\n".join([f"- {tool}" for tool in available_tools])
    missing_str = "\n".join([f"- {field}" for field in missing_fields])
    
    user_content = f"""Query: {query}

Missing information:
{missing_str}

Available tools:
{tools_str}

Select the tool that best retrieves the missing information."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
