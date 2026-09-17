import logging
from typing import Dict, Any, Optional

from ai.provider import AIProvider, get_ai_provider
from memory.memory_manager import MemoryManager
from security.permission_manager import PermissionManager
from tools.base_tool import BaseTool
from tools.task_tool import TaskTool
from tools.study_tool import StudyTool
from tools.schedule_tool import ScheduleTool
from tools.progress_tool import ProgressTool
from tools.profile_tool import ProfileTool
from tools.coding_tool import CodingTool

from core.context_manager import ContextManager
from core.router import IntentRouter
from core.planner import Planner
from core.decision_engine import DecisionEngine
from core.response_manager import ResponseManager

logger = logging.getLogger("tamizh_jarvis.core")


class JarvisCore:
    """Master agentic orchestrator for Tamizh JARVIS with 5-stage safe lifecycle execution."""

    def __init__(
        self,
        ai_provider: Optional[AIProvider] = None,
        memory_manager: Optional[MemoryManager] = None,
        permission_manager: Optional[PermissionManager] = None,
    ):
        self.ai = ai_provider or get_ai_provider()
        self.memory = memory_manager or MemoryManager()
        self.security = permission_manager or PermissionManager()

        self.context_manager = ContextManager(self.memory)
        self.router = IntentRouter(self.ai)
        self.planner = Planner()
        self.decision_engine = DecisionEngine()
        self.response_manager = ResponseManager()

        # Register Available Tools
        self.tools: Dict[str, BaseTool] = {
            "task_tool": TaskTool(self.memory),
            "study_tool": StudyTool(self.memory),
            "schedule_tool": ScheduleTool(self.memory),
            "progress_tool": ProgressTool(self.memory),
            "profile_tool": ProfileTool(self.memory),
            "coding_tool": CodingTool(),
        }

    async def initialize(self):
        """Pre-initialize persistent storage and memory."""
        await self.memory.initialize()

    async def handle(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main agentic entrypoint handling user message and returning structured response."""
        await self.initialize()
        user_message = message.strip()

        # Stage 1: Thinking (Understand & Context Formulation)
        active_context = await self.context_manager.build_context(user_message, context)

        # Stage 2: Planning (Intent Routing & Action Formulation)
        intent, confidence, entities = await self.router.route(user_message, active_context)
        logger.info("Routed intent: %s (confidence: %.2f)", intent, confidence)

        plan = self.planner.create_plan(intent, entities, active_context)

        tool_result = None
        tool_used = plan.tool_name
        action_name = plan.action
        memory_updated = False

        # Stage 3: Executing (Next Best Action or Security-Gated Tool Execution)
        if intent == "NEXT_BEST_ACTION":
            tool_result = self.decision_engine.compute_next_best_action(active_context)
            action_name = tool_result.get("action", "NEXT_BEST_ACTION")
            tool_used = "decision_engine"

        elif plan.tool_name and plan.tool_name in self.tools:
            tool = self.tools[plan.tool_name]

            # Stage 4: Verifying (Permission Gate & Security Authorization)
            is_confirmed = bool(context.get("confirmed", False)) if context else False
            authorized, reason, risk_level = self.security.evaluate(
                tool_name=plan.tool_name,
                action=plan.action,
                params=plan.params,
                user_confirmed=is_confirmed,
            )

            if not authorized:
                return {
                    "success": False,
                    "intent": intent,
                    "action": "PERMISSION_DENIED",
                    "response": f"Security restriction: {reason}",
                    "data": {"risk_level": risk_level.value, "reason": reason},
                    "toolUsed": tool_used,
                    "memoryUpdated": False,
                }

            # Safe Execution
            try:
                tool_result = await tool.execute(plan.params, active_context)
                action_name = tool_result.get("action", plan.action)
            except Exception as e:
                logger.error("Tool execution failed: %s", str(e), exc_info=True)
                return {
                    "success": False,
                    "intent": intent,
                    "action": "TOOL_ERROR",
                    "response": f"Tool execution encountered an error: {str(e)}",
                    "data": {},
                    "toolUsed": tool_used,
                    "memoryUpdated": False,
                }

        # Stage 5: Responding (Language Generation & Synthesis)
        raw_ai_text = None
        if not tool_result:
            system_prompt = (
                "You are Tamizh JARVIS, a personal agentic AI assistant. "
                "Tagline: Think. Plan. Execute. Learn. "
                "Be concise, clear, helpful, and proactive."
            )
            raw_ai_text = await self.ai.generate(prompt=user_message, system_prompt=system_prompt)

        response_text = self.response_manager.format_response(
            intent=intent,
            tool_result=tool_result,
            raw_ai_text=raw_ai_text,
            context=active_context,
        )

        # Memory Update (Context preservation without permanently storing raw unclassified noise)
        self.memory.record_interaction(
            sender="user",
            text=user_message,
            intent=intent,
        )
        self.memory.record_interaction(
            sender="jarvis",
            text=response_text,
            intent=intent,
            metadata=tool_result,
        )
        memory_updated = True

        return {
            "success": True,
            "intent": intent,
            "action": action_name,
            "response": response_text,
            "data": tool_result or {},
            "toolUsed": tool_used or "none",
            "memoryUpdated": memory_updated,
        }
