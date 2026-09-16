from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTool(ABC):
    """Base interface for all JARVIS tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable tool purpose."""
        pass

    @property
    def schema(self) -> Dict[str, Any]:
        """Input schema and argument definition."""
        return {}

    @abstractmethod
    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the tool operation securely and return structured data."""
        pass
