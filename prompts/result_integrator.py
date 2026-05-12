"""Prompt builder for result_integrator agent"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_result_integrator_prompt(
    known: Dict[str, Any],
    missing: List[str],
    latest_result: str,
) -> List[BaseMessage]:
    """
    Build result integration prompt.
    
    Decides whether to loop back for more tools or proceed to filtering.
    Completely generic — decision is based only on known/missing status.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = """You are an integration decision maker. Given current knowledge and a new tool result, decide:
- "loop" — more tools needed to answer the query confidently
- "proceed" — have enough information to proceed to analysis

Respond with ONLY "loop" or "proceed", nothing else."""
    
    known_str = "\n".join([f"{k}: {v}" for k, v in known.items()]) if known else "(none yet)"
    missing_str = "\n".join([f"- {field}" for field in missing]) if missing else "(none)"
    
    user_content = f"""Currently known:
{known_str}

Still missing:
{missing_str}

Latest tool result:
{latest_result}

Should we loop for more tools or proceed?"""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
