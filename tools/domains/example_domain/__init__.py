"""Example generic domain package.

Copy this folder to create a real domain package.
"""

from tools.registry import ToolRegistry
from tools.domains.example_domain.tool1 import Tool1
from tools.domains.example_domain.tool2 import Tool2

ToolRegistry.register("example_domain", "tool1", Tool1(name="tool1", description="Example tool 1"))
ToolRegistry.register("example_domain", "tool2", Tool2(name="tool2", description="Example tool 2"))
