from enum import Enum
from typing import Dict, Any


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskClassifier:
    """Classifies actions into 4 distinct security tiers."""

    @staticmethod
    def classify(tool_name: str, action: str, params: Dict[str, Any] = None) -> RiskLevel:
        tool_name = (tool_name or "").lower()
        action = (action or "").lower()
        params = params or {}

        # Critical / Prohibited Actions: Raw shell, direct destructive OS execution
        if any(keyword in action for keyword in ["shell", "terminal", "exec_cmd", "format_disk", "delete_all"]):
            return RiskLevel.CRITICAL
        if tool_name in ["os_tool", "shell_tool", "command_tool"]:
            return RiskLevel.CRITICAL

        # High Risk: Deletions, modifying security policies, file system mutations
        if any(keyword in action for keyword in ["delete", "remove", "drop", "overwrite", "change_setting"]):
            return RiskLevel.HIGH

        # Medium Risk: Creating/updating tasks, recording scores, external web requests
        if any(keyword in action for keyword in ["create", "add", "update", "record", "search_web"]):
            return RiskLevel.MEDIUM

        # Low Risk: Reading data, next-best-action computation, study recommendations
        return RiskLevel.LOW
