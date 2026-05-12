"""Router agent - classifies query into domain"""

import logging
import yaml
from pathlib import Path
from graph.state import AgentState
from prompts.router import build_router_prompt
from ollama import get_llm

logger = logging.getLogger(__name__)


async def router(state: AgentState) -> AgentState:
    """
    THE ONLY domain-aware agent.
    Classifies the query into a domain and sets state["domain"].
    """
    
    # Load available domains from config
    config_path = Path(__file__).parent.parent / "config" / "domains.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f) or {}
    available_domains = list((config.get("domains") or {}).keys())
    
    if not available_domains:
        logger.warning("No domains configured, defaulting to 'generic'")
        state["domain"] = "generic"
        return state
    
    # Build router prompt
    messages = build_router_prompt(state["query"], available_domains)
    
    # Get LLM response
    llm = get_llm()
    response = await llm.ainvoke(messages)
    
    # Extract domain from response
    domain = response.content.strip().lower()
    
    # Validate domain
    if domain not in available_domains and domain != "generic":
        logger.warning(f"Invalid domain '{domain}', defaulting to 'generic'")
        domain = "generic"
    
    state["domain"] = domain
    logger.info(f"Query routed to domain: {domain}")
    
    return state
