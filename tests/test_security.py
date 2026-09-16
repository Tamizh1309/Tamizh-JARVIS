from security.risk_classifier import RiskClassifier, RiskLevel
from security.action_validator import ActionValidator
from security.permission_manager import PermissionManager


def test_risk_classifier_tiers():
    # Prohibited shell attempt
    assert RiskClassifier.classify("shell_tool", "exec_cmd") == RiskLevel.CRITICAL
    assert RiskClassifier.classify("custom_tool", "rm -rf delete_all") == RiskLevel.CRITICAL

    # High risk
    assert RiskClassifier.classify("task_tool", "delete_task") == RiskLevel.HIGH

    # Medium risk
    assert RiskClassifier.classify("task_tool", "create") == RiskLevel.MEDIUM

    # Low risk
    assert RiskClassifier.classify("study_tool", "recommend") == RiskLevel.LOW


def test_action_validator_rejects_command_injection():
    valid, err = ActionValidator.validate("task_tool", "create", {"title": "Normal Task"})
    assert valid is True

    bad, err = ActionValidator.validate("task_tool", "create", {"title": "Test; rm -rf /"})
    assert bad is False
    assert "hazardous" in err


def test_permission_manager_blocks_critical():
    pm = PermissionManager()
    allowed, reason, risk = pm.evaluate("shell_tool", "exec_cmd", {})
    assert allowed is False
    assert risk == RiskLevel.CRITICAL
    assert "prohibited" in reason
