"""Tool registry for managing domain-specific tools."""

from typing import Dict, List, Optional
import logging

from tools.base_tool import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    """Central registry mapping domain names to BaseTool instances."""

    _registry: Dict[str, Dict[str, BaseTool]] = {}

    @classmethod
    def register(cls, domain: str, tool_name: str, tool: BaseTool) -> None:
        if domain not in cls._registry:
            cls._registry[domain] = {}

        cls._registry[domain][tool_name] = tool
        tool.domain = domain
        logger.info(f"Registered tool '{tool_name}' for domain '{domain}'")

    @classmethod
    def get_tools(cls, domain: str) -> Dict[str, BaseTool]:
        return cls._registry.get(domain, {})

    @classmethod
    def get_tool_names(cls, domain: str) -> List[str]:
        return list(cls.get_tools(domain).keys())

    @classmethod
    def get_tool(cls, domain: str, tool_name: str) -> Optional[BaseTool]:
        return cls.get_tools(domain).get(tool_name)

    @classmethod
    def list_domains(cls) -> List[str]:
        return list(cls._registry.keys())

    @classmethod
    def list_all_tools(cls) -> Dict[str, List[str]]:
        return {domain: cls.get_tool_names(domain) for domain in cls.list_domains()}
