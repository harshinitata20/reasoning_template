"""
Auto-loads all domain packages.
Each domain's __init__.py calls registry.register() on import.
"""

import importlib
import os
from pathlib import Path

DOMAINS_DIR = Path(__file__).parent

for domain_path in DOMAINS_DIR.iterdir():
    if domain_path.is_dir() and not domain_path.name.startswith("_") and (domain_path / "__init__.py").exists():
        try:
            importlib.import_module(f"tools.domains.{domain_path.name}")
        except Exception as e:
            print(f"Failed to load domain {domain_path.name}: {e}")
