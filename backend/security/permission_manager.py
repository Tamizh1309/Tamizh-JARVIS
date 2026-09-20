import logging
from typing import Tuple, Dict, Any
from security.risk_classifier import RiskClassifier, RiskLevel
from security.action_validator import ActionValidator
from config.settings import get_settings

logger = logging.getLogger("tamizh_jarvis.security.permissions")


class PermissionManager:
    """Gates and authorizes tool execution across the 5 risk tiers (READ, LOW, MEDIUM, HIGH, CRITICAL)."""

    def __init__(self):
        self.settings = get_settings()

    def evaluate(
        self,
        tool_name: str,
        action: str,
        params: Dict[str, Any] = None,
        user_confirmed: bool = False,
    ) -> Tuple[bool, str, RiskLevel]:
        params = params or {}

        # 1. Parameter Validation & Tool Allowlist & Prompt Injection Defense
        valid, err = ActionValidator.validate(tool_name, action, params)
        if not valid:
            logger.warning("Security rejection for %s:%s - %s", tool_name, action, err)
            return False, f"This action is strictly prohibited: {err}", RiskLevel.CRITICAL

        # 2. Risk Classification
        risk = RiskClassifier.classify(tool_name, action, params)

        # 3. Decision Logic across 5 tiers
        if risk == RiskLevel.CRITICAL:
            logger.error("BLOCKED critical/forbidden action attempt: %s:%s", tool_name, action)
            return False, "This action is strictly prohibited for security reasons.", risk

        if risk == RiskLevel.HIGH:
            if self.settings.SECURITY_REQUIRE_APPROVAL_FOR_HIGH_RISK and not user_confirmed:
                logger.info("High-risk action requires human confirmation: %s:%s", tool_name, action)
                return False, "High-risk action requires explicit user approval.", risk

        # READ, LOW, and confirmed/standard MEDIUM are permitted
        logger.debug("Action authorized [Tier: %s]: %s:%s", risk.value, tool_name, action)
        return True, "Authorized", risk
