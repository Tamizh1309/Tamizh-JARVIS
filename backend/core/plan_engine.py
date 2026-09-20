"""Multi-step plan execution engine for Tamizh JARVIS."""
import logging
import uuid
from enum import Enum
from typing import Dict, Any, List, Optional
from tools.base_tool import BaseTool
from security.permission_manager import PermissionManager
from security.risk_classifier import RiskLevel

logger = logging.getLogger("tamizh_jarvis.core.plan_engine")


class StepState(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"
    VERIFIED = "VERIFIED"


class ExecutionStep:
    """Represents an atomic step within an agent execution plan."""

    def __init__(
        self,
        step_id: int,
        tool: str,
        action: str,
        parameters: Optional[Dict[str, Any]] = None,
        description: str = ""
    ):
        self.step_id = step_id
        self.tool = tool
        self.action = action
        self.parameters = parameters or {}
        self.description = description or f"Execute {tool}:{action}"
        self.status = StepState.PENDING
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.verification_status: str = "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "tool": self.tool,
            "action": self.action,
            "parameters": self.parameters,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "verification_status": self.verification_status,
        }


class PlanExecution:
    """Encapsulates a multi-step execution lifecycle."""

    def __init__(self, query: str, steps: List[ExecutionStep]):
        self.plan_id = str(uuid.uuid4())[:8]
        self.query = query
        self.steps = steps
        self.status = StepState.PENDING
        self.current_step_index = 0
        self.partial_results: Dict[str, Any] = {}
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "query": self.query,
            "status": self.status.value,
            "total_steps": len(self.steps),
            "current_step_index": self.current_step_index,
            "steps": [s.to_dict() for s in self.steps],
            "partial_results": self.partial_results,
            "error": self.error,
        }


class ExecutionResult:
    """Result payload returned upon plan completion or safe termination."""

    def __init__(
        self,
        plan_id: str,
        success: bool,
        overall_status: StepState,
        steps: List[ExecutionStep],
        partial_results: Dict[str, Any],
        consolidated_data: Dict[str, Any],
        error: Optional[str] = None
    ):
        self.plan_id = plan_id
        self.success = success
        self.overall_status = overall_status
        self.steps = steps
        self.partial_results = partial_results
        self.consolidated_data = consolidated_data
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "success": self.success,
            "overall_status": self.overall_status.value,
            "steps": [s.to_dict() for s in self.steps],
            "partial_results": self.partial_results,
            "consolidated_data": self.consolidated_data,
            "error": self.error,
        }


class PlanExecutor:
    """Safe step-by-step executor with risk authorization and graceful failure."""

    def __init__(self, security: PermissionManager):
        self.security = security

    async def execute_plan(
        self,
        plan: PlanExecution,
        tools: Dict[str, BaseTool],
        context: Optional[Dict[str, Any]] = None,
        user_confirmed: bool = False
    ) -> ExecutionResult:
        plan.status = StepState.RUNNING
        context = context or {}
        consolidated: Dict[str, Any] = {}

        for idx, step in enumerate(plan.steps):
            plan.current_step_index = idx
            step.status = StepState.RUNNING

            # 1. Check Tool Registration
            if step.tool not in tools:
                step.status = StepState.FAILED
                step.error = f"Unregistered tool '{step.tool}' requested in plan."
                plan.error = step.error
                plan.status = StepState.FAILED
                self._skip_remaining(plan.steps, idx + 1)
                break

            tool_instance = tools[step.tool]

            # 2. Security Evaluation
            authorized, reason, risk_level = self.security.evaluate(
                tool_name=step.tool,
                action=step.action,
                params=step.parameters,
                user_confirmed=user_confirmed
            )

            if not authorized:
                step.status = StepState.BLOCKED
                step.error = f"Security Gate [{risk_level.value}]: {reason}"
                plan.error = step.error
                plan.status = StepState.BLOCKED
                self._skip_remaining(plan.steps, idx + 1)
                break

            # 3. Safe Step Execution
            try:
                # Provide previous step results into context for dynamic chaining
                step_context = dict(context)
                step_context["previous_step_results"] = plan.partial_results

                raw_output = await tool_instance.execute(step.parameters, step_context)
                step.result = raw_output

                # 4. Verification Check
                is_success = bool(raw_output.get("success", True)) if isinstance(raw_output, dict) else True
                if is_success:
                    step.status = StepState.VERIFIED
                    step.verification_status = "VERIFIED"
                    key = f"step_{step.step_id}_{step.action}"
                    plan.partial_results[key] = raw_output
                    consolidated[key] = raw_output
                else:
                    step.status = StepState.FAILED
                    step.error = raw_output.get("message") or raw_output.get("error") or "Tool returned failure"
                    step.verification_status = "FAILED"
                    plan.partial_results[f"step_{step.step_id}_failed"] = raw_output
                    plan.status = StepState.FAILED
                    plan.error = step.error
                    self._skip_remaining(plan.steps, idx + 1)
                    break

            except Exception as exc:
                logger.error("Step %d execution error: %s", step.step_id, str(exc), exc_info=True)
                step.status = StepState.FAILED
                step.error = f"Execution exception: {str(exc)}"
                step.verification_status = "FAILED"
                plan.error = step.error
                plan.status = StepState.FAILED
                self._skip_remaining(plan.steps, idx + 1)
                break

        if plan.status == StepState.RUNNING:
            plan.status = StepState.SUCCESS

        overall_success = plan.status in [StepState.SUCCESS, StepState.VERIFIED]

        return ExecutionResult(
            plan_id=plan.plan_id,
            success=overall_success,
            overall_status=plan.status,
            steps=plan.steps,
            partial_results=plan.partial_results,
            consolidated_data=consolidated,
            error=plan.error
        )

    @staticmethod
    def _skip_remaining(steps: List[ExecutionStep], start_index: int):
        for s in steps[start_index:]:
            s.status = StepState.SKIPPED
            s.verification_status = "SKIPPED"
