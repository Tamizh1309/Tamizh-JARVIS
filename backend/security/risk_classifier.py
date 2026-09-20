from enum import Enum
from typing import Dict, Any


class RiskLevel(str, Enum):
    READ = "READ"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskClassifier:
    """Classifies actions across all registered JARVIS tools into 5 distinct security tiers."""

    @staticmethod
    def classify(tool_name: str, action: str, params: Dict[str, Any] = None) -> RiskLevel:
        tool_name = (tool_name or "").lower().strip()
        action = (action or "").lower().strip()
        params = params or {}

        # 1. Critical / Prohibited Actions: Raw shell, direct destructive OS execution
        if any(kw in action for kw in ["shell", "terminal", "exec_cmd", "format_disk", "delete_all", "eval_unrestricted"]):
            return RiskLevel.CRITICAL
        if tool_name in ["os_tool", "shell_tool", "command_tool", "terminal_tool"]:
            return RiskLevel.CRITICAL

        # 2. High Risk: Deletions, modifying security policies, destructive mutations
        if any(kw in action for kw in ["delete", "remove", "drop", "overwrite", "change_setting"]):
            return RiskLevel.HIGH
        if tool_name == "task_tool" and action in ["delete", "delete_task", "task_delete"]:
            return RiskLevel.HIGH

        # 3. Medium Risk: Creating/updating tasks, updating career goals, recording study sessions, scheduling
        if any(kw in action for kw in ["create", "add", "update", "record", "set_goal", "set_career_goal", "complete", "log_session", "reminder", "schedule_notification", "apply_patch"]):
            return RiskLevel.MEDIUM
        if tool_name == "task_tool" and action in ["create", "update", "complete", "reminder"]:
            return RiskLevel.MEDIUM
        if tool_name == "profile_tool" and action in ["set_goal", "set_career_goal", "update_goal"]:
            return RiskLevel.MEDIUM
        if tool_name == "study_tool" and action in ["log_session", "record_session"]:
            return RiskLevel.MEDIUM

        # 4. Low Risk: Safe analysis, explanation, optimization, formatting, study recommendations, RAG queries
        if tool_name == "coding_tool" and action in ["explain", "review", "optimize", "dsa_practice", "generate_patch", "verify_patch"]:
            return RiskLevel.LOW
        if tool_name == "rag_tool":
            return RiskLevel.LOW
        if tool_name == "study_tool" and action in ["recommend", "gate_preparation", "mistake_analysis"]:
            return RiskLevel.LOW
        if tool_name == "progress_tool":
            return RiskLevel.LOW

        # 5. Read Tier: Querying RAG, listing tasks, reading memory, timetables, briefings
        if any(kw in action for kw in ["list", "get", "read", "briefing", "daily_briefing", "timetable", "search"]):
            return RiskLevel.READ

        # Default: Low risk
        return RiskLevel.LOW
