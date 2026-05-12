"""Example domain tool 2."""

from tools.base_tool import BaseTool


class Tool2(BaseTool):
    def run(self, **kwargs) -> str:
        query = kwargs.get("query", "")
        return f"tool2 output for: {query}"
