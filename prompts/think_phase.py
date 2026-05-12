"""Prompt builder for think_phase agent"""

from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_think_phase_prompt(
    query: str,
    context: Dict[str, Any],
) -> List[BaseMessage]:
    """
    Build think phase prompt for structured reasoning.
    
    This is completely generic — no domain references.
    Agent extracts: known facts, assumptions, missing information.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = """Perform structured reasoning on the query.

Output MUST include three XML sections:
1. <known> — facts clearly stated or implied in the query/context
2. <assumptions> — what you're assuming to be true
3. <missing> — what information you need to answer confidently

Be concise and specific."""
    
    context_str = "\n".join([f"{k}: {v}" for k, v in context.items()]) if context else "(no context)"
    
    user_content = f"""Query: {query}

Context:
{context_str}

Provide your structured reasoning with <known>, <assumptions>, and <missing> sections."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
