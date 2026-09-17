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

    @staticmethod
    def format_output(
        success: bool,
        action: str,
        data: Dict[str, Any],
        message: str,
    ) -> Dict[str, Any]:
        """Standard structured return contract across all tools."""
        res = {
            "success": success,
            "action": action,
            "data": data or {},
            "message": message,
        }
        if isinstance(data, dict):
            for k, v in data.items():
                if k not in res:
                    res[k] = v
        return res
