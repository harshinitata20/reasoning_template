"""Prompt builder for output_writer agent"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_output_writer_prompt(
    findings: List[Dict[str, Any]],
    risks: List[Dict[str, Any]],
    reasoning: str,
) -> List[BaseMessage]:
    """
    Build output writing prompt.
    
    Formats findings and risks into clear narrative.
    Completely generic.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = """You are an output formatter. Create a clear, concise summary of findings and risks.

Format:
## Key Findings
(numbered list of findings with scores)

## Risks & Implications
(numbered list of second-order risks)

## Reasoning
(brief explanation of the analysis)"""
    
    findings_str = "\n".join([f"- {f['text']} (score: {f['score']})" for f in findings])
    risks_str = "\n".join([f"- {r['trigger']} → {r['effect']} ({r['severity']})" for r in risks])
    
    user_content = f"""Findings:
{findings_str}

Risks:
{risks_str}

Reasoning:
{reasoning}

Create a clear summary."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
"""Prompt builder for second_order agent"""

from typing import List
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage


def build_second_order_prompt(findings_text: str) -> List[BaseMessage]:
    """
    Build second-order reasoning prompt.
    
    Extracts causal chains: What downstream effects do findings cause?
    Completely generic — no domain knowledge needed.
    
    Returns: List of LangChain messages for the LLM
    """
    
    system_prompt = """You are a second-order reasoning engine. For each finding, identify downstream effects and risks.

For each finding, provide:
- trigger: What finding caused this?
- effect: What downstream problem does it create?
- severity: critical | high | medium | low

Think about cascading impacts, not just immediate effects."""
    
    user_content = f"""Material findings:
{findings_text}

Identify second-order risks and cascading effects."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_content),
    ]
