"""Prompt builder for router agent"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
import yaml
from pathlib import Path


def build_router_prompt(query: str, available_domains: List[str]) -> List[BaseMessage]:
    """
    Build router prompt with available domains.
    
    The router prompt is the ONLY place that knows about domain names.
    Available domains come from config/domains.yaml.
    
    Returns: List of LangChain messages for the LLM
    """
    
    domain_list = "\n".join([f"- {domain}" for domain in available_domains])
    
    system_prompt = f"""You are a domain classifier. Analyze the user query and determine which domain it belongs to.

Available domains:
{domain_list}

Respond with ONLY the domain name in lowercase, nothing else. If the query doesn't match any domain clearly, respond with 'generic'."""
    
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query),
    ]
