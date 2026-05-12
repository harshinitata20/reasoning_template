"""Output writer agent - formats and writes final output"""

import logging
from graph.state import AgentState
from prompts.output_writer import build_output_writer_prompt
from llm import get_llm

logger = logging.getLogger(__name__)


async def output_writer(state: AgentState) -> AgentState:
    """
    Formats findings and risks into structured output.
    Output is already validated via PipelineOutput schema.
    """
    
    # Build output prompt
    messages = build_output_writer_prompt(
        state["findings"],
        state["second_order_risks"],
        state["reasoning"]
    )
    
    # Get LLM formatting
    llm = get_llm()
    response = await llm.ainvoke(messages)
    
    # Store formatted output in reasoning
    state["reasoning"] = response.content
    
    logger.info("Output written successfully")
    
    return state
