"""Unified Agent Orchestrator for Tamizh JARVIS."""
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from core.plan_engine import PlanExecution, ExecutionStep, ExecutionResult, PlanExecutor, StepState
from core.conversational_context import get_context_resolver
from core.fusion_engine import FusionEngine
from study.personalized_agent import PersonalizedStudyAgent
from tools.base_tool import BaseTool

logger = logging.getLogger("tamizh_jarvis.core.orchestrator")


class UnifiedOrchestrator:
    """
    Coordinates the end-to-end agentic lifecycle:
    AgentRequest -> Context Builder -> Intent Analysis -> Task Decomposition ->
    Execution Plan -> Security Validation -> Tool Execution -> Verification ->
    Memory Update -> Learning Loop -> Final Response.
    """

    def __init__(
        self,
        router,
        planner,
        security,
        memory,
        tools: Dict[str, BaseTool],
        ai_provider,
        response_manager
    ):
        self.router = router
        self.planner = planner
        self.security = security
        self.memory = memory
        self.tools = tools
        self.ai = ai_provider
        self.response_manager = response_manager
        self.plan_executor = PlanExecutor(security)
        self.context_resolver = get_context_resolver()
        self.fusion_engine = FusionEngine(memory)
        self.personalized_study = PersonalizedStudyAgent(memory)

    def is_multi_step_query(self, message: str) -> bool:
        """Detects whether user prompt requires multi-step decomposition."""
        text = (message or "").strip().lower()

        # Single-intent exclusions
        if text.startswith("create a reminder") or text.startswith("remind me to") or text.startswith("set a reminder"):
            return False
        if text.startswith("create a task") or text.startswith("add a task"):
            return False
        if text.startswith("complete ") or text.startswith("mark "):
            return False

        compound_markers = [
            "check my notes, identify weak",
            "check my notes and",
            "identify weak areas, create",
            "create a 2 hour revision plan, and remind me",
            "create a revision plan and remind me",
            "review this code and optimize",
            "review my code and optimize",
            "review and optimize",
        ]
        if any(m in text for m in compound_markers):
            return True

        has_notes = any(w in text for w in ["from my notes", "in my notes", "check my notes"])
        has_revision = any(w in text for w in ["revision plan", "2 hour plan", "weak areas"])
        has_reminder = any(w in text for w in ["and remind me", "and schedule a reminder"])
        if (has_notes and has_revision) or (has_revision and has_reminder):
            return True

        return False

    def decompose_multi_step_plan(self, message: str, context: Dict[str, Any]) -> List[ExecutionStep]:
        """Decomposes complex requests into ordered, verifiable ExecutionSteps."""
        text = message.lower()
        steps: List[ExecutionStep] = []
        step_id = 1

        topic = "Computer Science"
        for t in ["dbms", "operating systems", "os", "dsa", "algorithms", "computer networks", "cn", "gate"]:
            if t in text:
                topic = t.upper()
                break

        # Step 1: Query RAG Notes if requested
        if any(w in text for w in ["notes", "document", "docs", "from my notes"]):
            steps.append(ExecutionStep(
                step_id=step_id,
                tool="rag_tool",
                action="query",
                parameters={"query": f"{topic} exam notes concepts"},
                description=f"Query RAG knowledge base for {topic} notes and citations"
            ))
            step_id += 1

        # Step 2: Retrieve Weak Areas / Mistake Analysis if requested
        if any(w in text for w in ["weak", "mistake", "weak areas", "weakness"]):
            steps.append(ExecutionStep(
                step_id=step_id,
                tool="study_tool",
                action="mistake_analysis",
                parameters={"action": "mistake_analysis", "subject": topic},
                description=f"Analyze mistake records and weak areas for {topic}"
            ))
            step_id += 1

        # Step 3: Generate Revision Plan / Study Recommendation
        if any(w in text for w in ["revision plan", "plan", "revision", "2 hour", "hour"]):
            dur = 120 if "2 hour" in text else 45
            steps.append(ExecutionStep(
                step_id=step_id,
                tool="study_tool",
                action="recommend",
                parameters={"action": "recommend", "topic": topic, "duration": dur},
                description=f"Generate structured {dur}-minute revision plan for {topic}"
            ))
            step_id += 1

        # Step 4: Schedule Notification / Reminder if requested
        if any(w in text for w in ["remind", "reminder", "8 pm", "tomorrow"]):
            time_str = "tomorrow at 8 PM" if "8 pm" in text else "tomorrow at 9 AM"
            steps.append(ExecutionStep(
                step_id=step_id,
                tool="schedule_tool",
                action="schedule_notification",
                parameters={
                    "title": f"{topic} Revision Session",
                    "message": f"Time for scheduled {topic} study session.",
                    "scheduled_for": time_str
                },
                description=f"Schedule automated study reminder for {time_str}"
            ))
            step_id += 1

        # Step 5: Coding Review & Optimization multi-step
        if "review" in text and "optimize" in text:
            steps = [
                ExecutionStep(
                    step_id=1,
                    tool="coding_tool",
                    action="review",
                    parameters={"action": "review", "code": context.get("code", "")},
                    description="Perform AST static review and complexity analysis"
                ),
                ExecutionStep(
                    step_id=2,
                    tool="coding_tool",
                    action="optimize",
                    parameters={"action": "optimize", "code": context.get("code", "")},
                    description="Derive optimized code snippet and complexity reduction"
                )
            ]

        return steps

    async def execute_request(
        self,
        message: str,
        active_context: Dict[str, Any],
        user_confirmed: bool = False
    ) -> Dict[str, Any]:
        """Main orchestrator execution loop."""
        user_message = (message or "").strip()

        # Check for RAG + Memory Fusion query pattern
        if "from my notes" in user_message.lower() and any(w in user_message.lower() for w in ["revise", "should i", "retention"]):
            fusion_result = await self.fusion_engine.fuse_query(user_message, context=active_context)
            self.context_resolver.update_state_after_execution(
                intent="RAG_FUSION",
                action="fuse_query",
                params={"query": user_message},
                tool_result=fusion_result
            )
            await self.memory.record_learning(
                request_text=user_message,
                intent="RAG_FUSION",
                action="fuse_query",
                tool="rag_tool",
                success=True,
                metadata={"topic": fusion_result.get("topic")}
            )
            return {
                "success": True,
                "intent": "RAG_FUSION",
                "action": "fuse_query",
                "response": fusion_result.get("formatted_response"),
                "data": fusion_result,
                "toolUsed": "rag_fusion",
                "plan": None,
                "memoryUpdated": True,
            }

        # Multi-Step Execution Path
        if self.is_multi_step_query(user_message):
            steps = self.decompose_multi_step_plan(user_message, active_context)
            if steps:
                plan = PlanExecution(query=user_message, steps=steps)
                exec_result = await self.plan_executor.execute_plan(
                    plan=plan,
                    tools=self.tools,
                    context=active_context,
                    user_confirmed=user_confirmed
                )

                summary_lines = [f"### Multi-Step Execution Complete (Plan ID: {exec_result.plan_id})\n"]
                for s in exec_result.steps:
                    icon = "[VERIFIED]" if s.status == StepState.VERIFIED else ("[OK]" if s.status == StepState.SUCCESS else "[FAIL]")
                    summary_lines.append(f"- **Step {s.step_id}** [{s.tool}:{s.action}]: {icon} `{s.status.value}` - {s.description}")

                summary_lines.append("\n**Execution Details:**")
                for key, part in exec_result.partial_results.items():
                    if isinstance(part, dict) and part.get("message"):
                        summary_lines.append(f"- {part.get('message')}")

                response_text = "\n".join(summary_lines)

                await self.memory.record_learning(
                    request_text=user_message,
                    intent="MULTI_STEP_PLAN",
                    action="multi_step_execution",
                    tool="orchestrator",
                    success=exec_result.success,
                    metadata={"total_steps": len(steps), "plan_id": exec_result.plan_id}
                )

                return {
                    "success": exec_result.success,
                    "intent": "MULTI_STEP_PLAN",
                    "action": "multi_step_execution",
                    "response": response_text,
                    "data": exec_result.to_dict(),
                    "toolUsed": "orchestrator",
                    "plan": exec_result.to_dict(),
                    "memoryUpdated": True,
                }

        # Single-Step Unified Path
        intent, confidence, entities = await self.router.route(user_message, active_context)
        task_plan = self.planner.create_plan(intent, entities, active_context)

        if intent == "NEXT_BEST_ACTION":
            # Verify security
            authorized, reason, risk_level = self.security.evaluate(
                tool_name="study_tool",
                action="recommend",
                params=task_plan.params,
                user_confirmed=True,
            )
            if not authorized:
                return {
                    "success": False,
                    "intent": intent,
                    "action": "PERMISSION_DENIED",
                    "response": f"Security restriction: {reason}",
                    "data": {"risk_level": risk_level.value, "reason": reason},
                    "toolUsed": "decision_engine",
                    "memoryUpdated": False,
                }

            nba_result = await self.personalized_study.decide_next_study_action(context=active_context)
            response_text = self.response_manager.format_response(
                intent=intent,
                tool_result=nba_result,
                context=active_context
            )
            await self.memory.record_learning(
                request_text=user_message,
                intent=intent,
                action="next_best_action",
                tool="study_tool",
                success=True,
                metadata=nba_result
            )
            return {
                "success": True,
                "intent": intent,
                "action": "NEXT_BEST_ACTION",
                "response": response_text,
                "data": nba_result,
                "toolUsed": "decision_engine",
                "plan": None,
                "memoryUpdated": True,
            }

        tool_result = None
        tool_used = task_plan.tool_name or "none"
        action_name = task_plan.action

        if task_plan.tool_name:
            if task_plan.tool_name not in self.tools:
                logger.error("Architecture error: Planner requested unregistered tool '%s'", task_plan.tool_name)
                return {
                    "success": False,
                    "intent": intent,
                    "action": "MISSING_TOOL",
                    "response": f"Requested tool '{task_plan.tool_name}' is not registered in JarvisCore.",
                    "data": {"requested_tool": task_plan.tool_name},
                    "toolUsed": task_plan.tool_name,
                    "memoryUpdated": False,
                }

            tool = self.tools[task_plan.tool_name]

            # Security authorization gate
            is_confirmed = user_confirmed or bool(active_context.get("confirmed", False))
            authorized, reason, risk_level = self.security.evaluate(
                tool_name=task_plan.tool_name,
                action=task_plan.action,
                params=task_plan.params,
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
                tool_result = await tool.execute(task_plan.params, active_context)
                action_name = tool_result.get("action", task_plan.action) if isinstance(tool_result, dict) else task_plan.action
            except Exception as e:
                logger.error("Tool execution failed: %s", str(e), exc_info=True)
                return {
                    "success": False,
                    "intent": intent,
                    "action": "TOOL_ERROR",
                    "response": f"Tool execution encountered an error: {str(e)}",
                    "data": {"error": str(e)},
                    "toolUsed": tool_used,
                    "memoryUpdated": False,
                }

        raw_ai_text = None
        if not tool_result:
            system_prompt = (
                "You are Tamizh JARVIS, a personal agentic AI assistant. "
                "Tagline: Think. Plan. Execute. Learn. "
                "Be concise, clear, helpful, and proactive."
            )
            try:
                raw_ai_text = await self.ai.generate(prompt=user_message, system_prompt=system_prompt)
            except Exception:
                raw_ai_text = "I received your request. How may I assist your tasks or study?"

        response_text = self.response_manager.format_response(
            intent=intent,
            tool_result=tool_result,
            raw_ai_text=raw_ai_text,
            context=active_context
        )

        self.context_resolver.update_state_after_execution(
            intent=intent,
            action=action_name,
            params=task_plan.params,
            tool_result=tool_result
        )

        await self.memory.record_learning(
            request_text=user_message,
            intent=intent,
            action=action_name,
            tool=tool_used,
            success=True,
            metadata=tool_result if isinstance(tool_result, dict) else {}
        )

        return {
            "success": True,
            "intent": intent,
            "action": action_name,
            "response": response_text,
            "data": tool_result or {},
            "toolUsed": tool_used,
            "plan": None,
            "memoryUpdated": True,
        }
