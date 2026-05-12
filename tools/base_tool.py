"""Base tool class for domain-specific implementations"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseTool(ABC):
    """
    Abstract base class for all domain-specific tools.
    All tools must inherit and implement the run() method.
    Returns plain text strings.
    """
    
    def __init__(self, name: str, description: str):
        """Initialize a tool"""
        self.name = name
        self.description = description
        self.domain: str = ""  # Set during registration
    
    @abstractmethod
    def run(self, **kwargs) -> str:
        """
        Execute the tool and return plain text result.
        
        Args:
            **kwargs: Tool-specific arguments
        
        Returns:
            Plain string output from the tool
        """
        pass
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def run_with_retry(self, **kwargs) -> str:
        """Execute tool with automatic retry on failure"""
        return self.run(**kwargs)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, domain={self.domain})"
