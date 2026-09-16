from typing import Dict, Any, Tuple


class ActionValidator:
    """Validates parameters for security and schema conformance."""

    @staticmethod
    def validate(tool_name: str, action: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        if not isinstance(params, dict):
            return False, "Parameters must be a dictionary."

        # Reject any parameters attempting shell injection or dangerous system paths
        for key, val in params.items():
            if isinstance(val, str):
                forbidden = [";", "&&", "||", "`", "$(", "rm -rf", "cmd.exe", "powershell.exe"]
                if any(f in val.lower() for f in forbidden):
                    return False, f"Potentially hazardous sequence detected in parameter '{key}'."

        return True, "Valid"
