"""Public entry point for the analysis agent pipeline."""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from graph.builder import build_graph
from graph.state import AgentState
from output.schema import Finding, PipelineMetadata, PipelineOutput, Risk, ToolResult
from output.writer import write_output
import tools.domains  

logger = logging.getLogger(__name__)


async def run_pipeline(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    domain_hint: Optional[str] = None,
) -> PipelineOutput:
    """
    Public entry point for the analysis pipeline.
    
    Args:
        query: User query to analyze
        context: Additional context (optional)
        domain_hint: Force a specific domain (optional, router ignores if provided)
    
    Returns:
        Validated PipelineOutput ready for consumption
    """
    
    run_id = str(uuid.uuid4())[:8]
    start_time = datetime.utcnow()
    
    logger.info(f"Starting pipeline run {run_id}: {query[:50]}...")
    
    try:
        # Initialize state
        initial_state: AgentState = {
            "query": query,
            "context": context or {},
            "run_id": run_id,
            "domain": domain_hint or "",  # Router will set this
            "known": {},
            "assumptions": [],
            "missing": [],
            "available_tools": [],
            "selected_tool": None,
            "tool_results": [],
            "loop_decision": None,
            "loop_count": 0,
            "findings": [],
            "second_order_risks": [],
            "reasoning": "",
            "output_path": None,
        }
        
        # Build and invoke the graph
        graph = build_graph()
        final_state = await graph.ainvoke(initial_state)
        
        # Create PipelineOutput
        duration = (datetime.utcnow() - start_time).total_seconds()
        
        findings = [Finding(**finding) for finding in final_state.get("findings", [])]
        risks = [Risk(**risk) for risk in final_state.get("second_order_risks", [])]
        tool_results = [
            ToolResult(tool_name=result["tool_name"], output=result["result"], cached=result.get("cached", False))
            for result in final_state.get("tool_results", [])
        ]

        output = PipelineOutput(
            domain=final_state.get("domain", "generic"),
            query=query,
            findings=findings,
            risks=risks,
            tool_results=tool_results,
            reasoning=final_state.get("reasoning", ""),
            metadata=PipelineMetadata(
                run_id=run_id,
                domain=final_state.get("domain", "generic"),
                query=query,
                context=context or {},
                loop_count=final_state.get("loop_count", 0),
                total_tools_executed=len(tool_results),
                execution_time_seconds=duration,
            ),
        )
        
        # Write output to filesystem
        output_path = write_output(output)
        output.output_path = output_path
        
        logger.info(f"Pipeline run {run_id} completed in {duration:.2f}s")
        
        return output
        
    except Exception as e:
        logger.error(f"Pipeline run {run_id} failed: {e}", exc_info=True)
        raise


# Sync wrapper for environments that don't support async
def run_pipeline_sync(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    domain_hint: Optional[str] = None,
) -> PipelineOutput:
    """Sync wrapper for run_pipeline"""
    return asyncio.run(run_pipeline(query, context, domain_hint))
