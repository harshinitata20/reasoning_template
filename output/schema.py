"""Output schemas for the generic analysis agent pipeline"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Result from a single tool execution"""
    
    tool_name: str = Field(..., description="Name of the tool that was executed")
    output: str = Field(..., description="Plain text output from the tool")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(default=False, description="Whether result was from cache")


class Finding(BaseModel):
    """A material finding from the analysis"""
    
    text: str = Field(..., description="Description of the finding")
    score: float = Field(..., ge=1, le=5, description="Materiality score 1-5")
    category: str = Field(..., description="Category of finding (e.g., risk, opportunity)")
    tool_source: Optional[str] = Field(None, description="Which tool generated this")


class Risk(BaseModel):
    """Second-order risk derived from findings"""
    
    trigger: str = Field(..., description="What finding triggered this risk")
    effect: str = Field(..., description="What downstream effect this causes")
    severity: str = Field(..., description="Severity: critical, high, medium, low")


class PipelineMetadata(BaseModel):
    """Metadata about the pipeline run"""
    
    run_id: str
    domain: str
    query: str
    context: Dict[str, Any] = Field(default_factory=dict)
    loop_count: int
    total_tools_executed: int
    execution_time_seconds: float


class PipelineOutput(BaseModel):
    """Final validated output from the pipeline"""
    
    domain: str = Field(..., description="Domain the query was routed to")
    query: str = Field(..., description="Original user query")
    findings: List[Finding] = Field(default_factory=list, description="Material findings")
    risks: List[Risk] = Field(default_factory=list, description="Second-order risks")
    tool_results: List[ToolResult] = Field(default_factory=list, description="All tool executions")
    reasoning: str = Field(default="", description="Agent's reasoning process")
    metadata: PipelineMetadata = Field(..., description="Run metadata")
    output_path: Optional[str] = Field(None, description="Where this output was written")
