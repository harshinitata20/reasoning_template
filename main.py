#!/usr/bin/env python
"""Main entry point for the Reasoning Pipeline."""

import argparse
import json
import logging
import sys
from typing import Optional

import tools.domains  # ensure domains are loaded
from config.settings import settings
from analysis_agent.pipeline import run_pipeline_sync
from tools.registry import ToolRegistry

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Run the Reasoning Pipeline for analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Analyze security risks" --domain example_domain
  python main.py "Demo query" --context '{"source":"cli"}'
  python main.py "Test" --debug
  python main.py --list-tools
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        default='Demo analysis run',
        help='The query to analyze (default: "Demo analysis run")'
    )
    
    parser.add_argument(
        '--domain',
        type=str,
        default=None,
        help='Force a specific domain (e.g., example_domain). If not specified, router will determine.'
    )
    
    parser.add_argument(
        '--context',
        type=str,
        default='{"source":"cli"}',
        help='Additional context as JSON string (default: \'{"source":"cli"}\')'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--list-tools',
        action='store_true',
        help='List available tools and exit'
    )
    
    parser.add_argument(
        '--output-json',
        action='store_true',
        help='Output result as JSON only (no logging)'
    )
    
    return parser.parse_args()


def list_tools():
    """List all available tools."""
    all_tools = ToolRegistry.list_all_tools()
    print("\nAvailable Tools by Domain:")
    print("=" * 50)
    for domain, tools in all_tools.items():
        print(f"\n{domain}:")
        for tool in tools:
            print(f"  - {tool}")
    print("\n" + "=" * 50)


def parse_context(context_str: str) -> dict:
    """Parse context from JSON string."""
    try:
        return json.loads(context_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse context JSON: {e}")
        return {"source": "cli"}


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # List tools if requested
    if args.list_tools:
        list_tools()
        sys.exit(0)
    
    # Configure debug mode
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Parse context
    context = parse_context(args.context)
    
    # Log startup info
    if not args.output_json:
        logger.info(f"Starting pipeline with query: {args.query}")
        logger.info(f"Domain hint: {args.domain or 'auto-detect'}")
        logger.info(f"Context: {context}")
        logger.info(f"vLLM server: {settings.VLLM_BASE_URL}")
        logger.info(f"Model: {settings.VLLM_MODEL}")
    
    try:
        # Run the pipeline
        result = run_pipeline_sync(
            query=args.query,
            context=context,
            domain_hint=args.domain
        )
        
        # Output result
        if args.output_json:
            # JSON output only
            output = {
                "status": "success",
                "data": {
                    "domain": result.domain,
                    "query": result.query,
                    "findings": [
                        {
                            "text": f.text,
                            "score": f.score,
                            "category": f.category
                        }
                        for f in result.findings
                    ],
                    "risks": [
                        {
                            "text": r.text,
                            "severity": r.severity,
                            "category": r.category
                        }
                        for r in result.risks
                    ],
                    "reasoning": result.reasoning,
                    "metadata": {
                        "run_id": result.metadata.run_id,
                        "domain": result.metadata.domain,
                        "loop_count": result.metadata.loop_count,
                        "tools_executed": result.metadata.total_tools_executed,
                        "execution_time_seconds": result.metadata.execution_time_seconds
                    }
                }
            }
            print(json.dumps(output, indent=2))
        else:
            # Pretty output
            logger.info(f"\n{'='*60}")
            logger.info(f"Pipeline completed in {result.metadata.execution_time_seconds:.2f}s")
            logger.info(f"Run ID: {result.metadata.run_id}")
            logger.info(f"Domain: {result.domain}")
            logger.info(f"Tools executed: {result.metadata.total_tools_executed}")
            logger.info(f"Loop iterations: {result.metadata.loop_count}")
            logger.info(f"\nFindings: {len(result.findings)}")
            for i, finding in enumerate(result.findings, 1):
                logger.info(f"  {i}. [{finding.score:.1f}] {finding.text}")
            logger.info(f"\nRisks: {len(result.risks)}")
            for i, risk in enumerate(result.risks, 1):
                logger.info(f"  {i}. [{risk.severity}] {risk.text}")
            logger.info(f"\nOutput saved to: {result.output_path}")
            logger.info(f"{'='*60}\n")
            print(result)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Pipeline execution failed: {e}")
        if args.output_json:
            print(json.dumps({
                "status": "error",
                "error": str(e)
            }, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    main()
