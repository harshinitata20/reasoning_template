"""Prompt builder for materiality_filter agent"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_materiality_filter_prompt(
    findings_text: str,
    threshold: float = 3.0,
) -> List[BaseMessage]:
    """
    Build materiality filtering prompt.
    
    Scores findings 1-5 by business impact.
    Completely generic — rubric is prompt-driven, no domain terms.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = f"""You are a materiality filter. Score findings 1-5 by business impact:
- 1: Trivial, ignore
- 2: Minor, note but non-critical
- 3: Moderate, important for decisions
- 4: Significant, drives strategy
- 5: Critical, game-changing

Threshold: {threshold} (keep only scores >= {threshold})

Output format:
[{{"text": "...", "score": N, "category": "..."}}]"""
    
    user_content = f"""Findings to score:
{findings_text}

Score each finding and filter below threshold {threshold}."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
