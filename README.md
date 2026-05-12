# Reasoning Template

A multi-agent LLM reasoning pipeline for structured analysis and decision-making, powered by **LangGraph** and **vLLM**.

## Overview

This project implements a sophisticated reasoning framework that:
- Routes queries to domain-specific analyzers
- Performs structured thinking phases with XML-based reasoning
- Executes domain-specific tools intelligently
- Scores findings by materiality (business impact)
- Identifies second-order risks and cascading effects
- Generates JSON-formatted analysis reports

Perfect for compliance analysis, risk assessment, audit workflows, and custom reasoning tasks.

## Features

✅ **Multi-Agent Architecture** - Specialized agents for routing, thinking, tool selection, filtering, and integration  
✅ **Domain-Based Routing** - Automatic classification of queries into domains with domain-specific tools  
✅ **Structured Reasoning** - XML-formatted thinking phases capturing known facts, assumptions, and missing info  
✅ **Materiality Scoring** - Automatic ranking of findings (1-5 scale) with configurable thresholds  
✅ **Risk Analysis** - Second-order reasoning to identify cascading risks and dependencies  
✅ **vLLM Integration** - Uses local/remote vLLM servers with fallback to deterministic responses  
✅ **CLI Entry Point** - Production-ready command-line interface with multiple output modes  
✅ **JSON Output** - Structured output schema for programmatic consumption  

## Installation

### Prerequisites
- Python 3.13+
- vLLM server (local or remote) or fallback mode for development

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/harshinitata20/reasoning_template.git
   cd reasoning_template
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure vLLM connection** (optional - uses defaults if not set)
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your vLLM server details:
   ```
   vLLM_URL=http://10.88.0.201:11434/api/chat
   vLLM_MODEL=qwen3.5:9b
   ```

## Quick Start

### Run a Default Analysis
```bash
python main.py
```
Runs the pipeline with the demo query "Demo analysis run" on the `example_domain`.

### Run with Custom Query
```bash
python main.py "Analyze the new data processing workflow"
```

### Specify a Domain
```bash
python main.py "Your query here" --domain example_domain
```

### Add Context
```bash
python main.py "Your query" --context '{"source":"audit","date":"2026-05-12"}'
```

### Debug Mode (Verbose Logging)
```bash
python main.py "Your query" --debug
```

### JSON Output Only
```bash
python main.py "Your query" --output-json
```
Returns only structured JSON (no logging output). Ideal for automation.

### List Available Tools
```bash
python main.py --list-tools
```
Shows all tools available by domain.

## Configuration

### Environment Variables (`.env`)
```ini
# vLLM Server
vLLM_URL=http://10.88.0.201:11434/api/chat
vLLM_MODEL=qwen3.5:9b

# Model Parameters
vLLM_TEMPERATURE=0.2
vLLM_MAX_TOKENS=2048
vLLM_TIMEOUT_SECONDS=300

# Fallback Behavior
USE_LOCAL_FALLBACK=False
FALLBACK_ON_ERROR=True

# Analysis Settings
MATERIALITY_THRESHOLD=3.0
MAX_LOOP_ITERATIONS=5

# Logging
LOG_LEVEL=DEBUG
DEBUG=True
```

### Settings File
Edit `config/settings.py` for permanent configuration changes.

## Project Structure

```
reasoning_template/
├── main.py                 # CLI entry point
├── vLLM.py              # vLLM client adapter & LLM wrapper
├── config/
│   ├── settings.py        # Pydantic-based configuration
│   └── domains.yaml       # Domain definitions
├── agents/                # Multi-agent pipeline modules
│   ├── router.py          # Route queries to domains
│   ├── think_phase.py     # Structured reasoning
│   ├── tool_selector.py   # Select tools for execution
│   ├── tool_executor.py   # Execute selected tools
│   ├── materiality_filter.py  # Score and filter findings
│   ├── second_order.py    # Risk analysis
│   └── output_writer.py   # Format final output
├── graph/                 # LangGraph state machine
│   ├── state.py           # AgentState definition
│   ├── builder.py         # Graph construction
│   └── edges.py           # Conditional edge logic
├── analysis_agent/
│   └── pipeline.py        # Public pipeline entry point
├── tools/                 # Tool registry and domains
│   ├── base_tool.py       # BaseTool interface
│   ├── registry.py        # Tool discovery & registration
│   └── domains/
│       └── example_domain/    # Example domain
│           ├── tool1.py
│           └── tool2.py
├── prompts/               # Agent prompt templates
├── output/                # Output schema & writer
└── requirements.txt       # Python dependencies
```

## Adding Custom Domains

### 1. Create Domain Directory
```bash
mkdir tools/domains/my_domain
touch tools/domains/my_domain/__init__.py
```

### 2. Implement Tools
Create `tools/domains/my_domain/my_tool.py`:
```python
from tools.base_tool import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "Does something specific to my domain"
    
    def execute(self, query: str) -> str:
        return f"Analysis result for: {query}"

# Auto-register on import
__all__ = [MyTool]
```

### 3. Register in Domain Config
Add to `config/domains.yaml`:
```yaml
my_domain:
  description: "Custom domain for my analysis"
  tools:
    - my_tool
```

### 4. Test
```bash
python main.py "Test query" --domain my_domain
```

## Architecture

### Agent Pipeline Flow
```
1. Router Agent
   └─ Classify query → domain

2. Think Phase Agent
   └─ Structured reasoning → (known, assumptions, missing)

3. Tool Selection Loop (max 5 iterations)
   ├─ Tool Selector Agent
   │  └─ Choose best tool for missing info
   ├─ Tool Executor Agent
   │  └─ Execute tool
   └─ Result Integrator Agent
      └─ Decide: loop or proceed?

4. Materiality Filter Agent
   └─ Score findings (1-5) → filter by threshold

5. Second-Order Analysis Agent
   └─ Identify risks and cascading effects

6. Output Writer Agent
   └─ Format final results

7. Output Writer Module
   └─ Write JSON to output/shared/{domain}/{run_id}.json
```

### LLM Integration
- **Primary**: vLLM server (local or remote) via OpenAI-compatible `/api/chat` endpoint
- **Fallback**: Deterministic local client (development mode)
- **Model**: qwen3.5:9b (9.7B parameters, optimized for reasoning)

## Output Format

### JSON Output Schema
```json
{
  "status": "success|error",
  "data": {
    "domain": "example_domain",
    "query": "Original query text",
    "findings": [
      {
        "text": "Finding description",
        "score": 3.0,
        "category": "generic"
      }
    ],
    "risks": [
      {
        "description": "Risk description",
        "severity": "high|medium|low"
      }
    ],
    "reasoning": "Full reasoning chain and analysis",
    "metadata": {
      "run_id": "d07c2c96",
      "execution_time_seconds": 0.51,
      "tools_executed": 5,
      "loop_iterations": 5
    },
    "output_path": "output/shared/example_domain/d07c2c96.json"
  }
}
```

## Troubleshooting

### Issue: "404 on /v1 endpoint"
**Solution**: Update `.env` with correct vLLM endpoint:
```ini
vLLM_URL=http://10.88.0.201:11434/api/chat
```

### Issue: "TimeoutError" from vLLM
**Solution**: Increase timeout in `.env`:
```ini
vLLM_TIMEOUT_SECONDS=300
```

### Issue: Model not found
**Solution**: List available vLLM models:
```bash
curl http://10.88.0.201:11434/api/tags
```
Update `vLLM_MODEL` in `.env` to available model.

### Issue: Fallback to local client (no real LLM responses)
**Solution**: Verify vLLM server is running and reachable:
```bash
curl http://10.88.0.201:11434/api/chat -X POST -d '{"model":"qwen3.5:9b","messages":[{"role":"user","content":"test"}]}'
```

## Dependencies

- **langchain** ≥0.1.0 - LLM framework
- **langchain-community** ≥0.0.10 - Community integrations
- **langgraph** ≥0.0.20 - Graph-based workflows
- **pydantic** ≥2.0 - Data validation & settings
- **pyyaml** ≥6.0 - YAML parsing
- **requests** ≥2.31.0 - HTTP client
- **python-dotenv** ≥1.0.0 - Environment variable management
- **aiohttp** ≥3.8.0 - Async HTTP

See `requirements.txt` for exact versions.

## Development

### Run Tests
```bash
pytest tests/
```

### Enable Debug Logging
```python
# In config/settings.py
DEBUG = True
LOG_LEVEL = "DEBUG"
```

### Check Code Quality
```bash
# Type checking
mypy .

# Linting
pylint agents/ tools/ analysis_agent/
```

## Examples

### Compliance Analysis
```bash
python main.py "Review new data privacy policy for GDPR compliance" \
  --domain compliance \
  --context '{"policy_version":"3.2","jurisdiction":"EU"}'
```

### Risk Assessment
```bash
python main.py "Identify operational risks in new supply chain" \
  --domain risk_management \
  --output-json > risk_report.json
```

### Audit Workflow
```bash
python main.py "Audit internal control effectiveness" \
  --domain audit \
  --context '{"audit_year":"2026","scope":"financial"}'
```

## License

MIT - See LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with tests

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review output logs (DEBUG=True in `.env`)
3. Open an issue on GitHub

---

**Built with ❤️ using LangGraph and vLLM**
