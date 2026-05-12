"""Output writer for pipeline results"""

import json
import logging
import os
from pathlib import Path
from datetime import datetime
from typing import Optional
from output.schema import PipelineOutput
from config.settings import settings

logger = logging.getLogger(__name__)


class OutputWriter:
    """Writes validated PipelineOutput to filesystem"""
    
    @staticmethod
    def write(output: PipelineOutput) -> str:
        """
        Write output to filesystem atomically.
        Path pattern: {SHARED_FS_PATH}/{domain}/{run_id}.json
        """
        # Create domain directory
        domain_dir = Path(settings.SHARED_FS_PATH) / output.domain
        domain_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        run_id = output.metadata.run_id
        output_file = domain_dir / f"{run_id}.json"
        
        # Write atomically: write to temp file, then rename
        temp_file = output_file.with_suffix(".tmp")
        
        try:
            # Serialize to JSON
            json_str = output.model_dump_json(indent=2)
            
            # Write to temp file
            with open(temp_file, "w") as f:
                f.write(json_str)
            
            # Atomic rename
            temp_file.replace(output_file)
            
            # Update output_path in the output object
            output.output_path = str(output_file)
            
            logger.info(f"Output written to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to write output to {output_file}: {e}")
            if temp_file.exists():
                temp_file.unlink()
            raise


def write_output(output: PipelineOutput) -> str:
    """Write output to filesystem (convenience function)"""
    return OutputWriter.write(output)
