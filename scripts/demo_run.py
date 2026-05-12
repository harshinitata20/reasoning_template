import logging
logging.basicConfig(level=logging.INFO)

import tools.domains  # ensure domains are loaded
from tools.registry import ToolRegistry
print('registered:', ToolRegistry.list_all_tools())

from analysis_agent.pipeline import run_pipeline_sync
out = run_pipeline_sync('Demo tool run', {'source': 'demo'})
print(out)
