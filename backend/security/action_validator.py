import re
from typing import Dict, Any, Tuple

ALLOWED_TOOLS = {
    "study_tool",
    "task_tool",
    "profile_tool",
    "progress_tool",
    "coding_tool",
    "schedule_tool",
    "rag_tool",
    "decision_engine",
    "orchestrator",
}

PROMPT_INJECTION_PATTERNS = [
    r"ignore (?:all )?previous instructions",
    r"disregard (?:all )?prior instructions",
    r"bypass (?:all )?safety",
    r"you are now in developer mode",
    r"dan mode",
    r"system override",
    r"act as (?:an? )?unrestricted",
    r"reveal (?:your )?system prompt",
]


class ActionValidator:
    """Validates parameters, checks tool allowlist, and defends against prompt/command injection."""

    @staticmethod
    def validate(tool_name: str, action: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        t_clean = (tool_name or "").strip().lower()
        if t_clean and t_clean not in ALLOWED_TOOLS:
            return False, f"Tool '{tool_name}' is not in the authorized JARVIS tool allowlist."

        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary."

        # Shell and path injection checks
        forbidden_shell = [";", "&&", "||", "`", "$(", "rm -rf", "cmd.exe", "powershell.exe", "/etc/passwd"]
        for key, val in params.items():
            if isinstance(val, str):
                v_lower = val.lower()
                if any(f in v_lower for f in forbidden_shell):
                    return False, f"Potentially hazardous sequence detected in parameter '{key}'."

                for pattern in PROMPT_INJECTION_PATTERNS:
                    if re.search(pattern, v_lower):
                        return False, f"Potential prompt injection pattern detected in parameter '{key}'."

        return True, "Valid"
