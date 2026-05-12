"""Example domain tool 1."""

from tools.base_tool import BaseTool


class Tool1(BaseTool):
    def run(self, **kwargs) -> str:
        query = kwargs.get("query", "")
        return f"tool1 output for: {query}"
