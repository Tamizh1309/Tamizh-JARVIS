"""Master agentic orchestrator for Tamizh JARVIS with unified multi-step and 5-stage lifecycle execution."""
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
from tools.rag_tool import RAGTool

from core.context_manager import ContextManager
from core.router import IntentRouter
from core.planner import Planner
from core.decision_engine import DecisionEngine
from core.response_manager import ResponseManager
from core.orchestrator import UnifiedOrchestrator

logger = logging.getLogger("tamizh_jarvis.core")


class JarvisCore:
    """Master agentic orchestrator for Tamizh JARVIS with safe lifecycle execution."""

    def __init__(
        self,
        ai_provider: Optional[AIProvider] = None,
        memory_manager: Optional[MemoryManager] = None,
        permission_manager: Optional[PermissionManager] = None,
        router: Optional[IntentRouter] = None,
        planner: Optional[Planner] = None,
        context_manager: Optional[ContextManager] = None,
        response_manager: Optional[ResponseManager] = None,
    ):
        self.ai = ai_provider or get_ai_provider()
        self.ai_provider = self.ai
        self.memory = memory_manager or MemoryManager()
        self.security = permission_manager or PermissionManager()

        self.context_manager = context_manager or ContextManager(self.memory)
        self.router = router or IntentRouter(self.ai)
        self.planner = planner or Planner()
        self.decision_engine = DecisionEngine()
        self.response_manager = response_manager or ResponseManager()

        # Pre-register all authorized tools
        self.tools: Dict[str, BaseTool] = {
            "task_tool": TaskTool(self.memory),
            "study_tool": StudyTool(self.memory),
            "schedule_tool": ScheduleTool(self.memory),
            "progress_tool": ProgressTool(self.memory),
            "profile_tool": ProfileTool(self.memory),
            "coding_tool": CodingTool(),
            "rag_tool": RAGTool(),
        }

        # Unified Orchestrator
        self.orchestrator = UnifiedOrchestrator(
            router=self.router,
            planner=self.planner,
            security=self.security,
            memory=self.memory,
            tools=self.tools,
            ai_provider=self.ai,
            response_manager=self.response_manager
        )

    def register_tool(self, tool: BaseTool) -> None:
        """Registers an authorized tool."""
        self.tools[tool.name] = tool
        if hasattr(self, "orchestrator") and self.orchestrator:
            self.orchestrator.tools[tool.name] = tool

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Returns the tool instance if registered in JARVIS."""
        return self.tools.get(tool_name)

    def has_tool(self, tool_name: str) -> bool:
        """Checks if a tool is registered in JARVIS."""
        return tool_name in self.tools

    def validate_tool_registry(self) -> bool:
        """Validates that all registered tools conform to BaseTool interface."""
        for name, tool in self.tools.items():
            if not isinstance(tool, BaseTool):
                return False
            if tool.name != name:
                return False
        return True

    def verify_tool_registry(self) -> bool:
        """Alias for validate_tool_registry."""
        return self.validate_tool_registry()

    async def initialize(self):
        """Pre-initialize persistent storage and memory."""
        await self.memory.initialize()

    async def handle(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main agentic entrypoint handling user message through the unified orchestrator."""
        user_message = (message or "").strip()

        if not user_message:
            return {
                "success": False,
                "intent": "GENERAL_CHAT",
                "action": "EMPTY_MESSAGE",
                "response": "Empty message received. How may I assist your productivity or study today?",
                "data": {},
                "toolUsed": "none",
                "memoryUpdated": False,
            }

        try:
            await self.initialize()

            # Build enriched context with conversational entity tracking
            active_context = await self.context_manager.build_context(user_message, context)

            # Sync tools to orchestrator in case test manipulated self.tools
            self.orchestrator.tools = self.tools

            # Process through Unified Orchestrator
            result = await self.orchestrator.execute_request(user_message, active_context)

            # Record interaction to conversation memory
            try:
                self.memory.record_interaction(
                    sender="user",
                    text=user_message,
                    intent=result.get("intent", "GENERAL_CHAT"),
                )
                self.memory.record_interaction(
                    sender="jarvis",
                    text=result.get("response", ""),
                    intent=result.get("intent", "GENERAL_CHAT"),
                    metadata=result.get("data"),
                )
            except TypeError:
                # Handle 2-arg signature fallback if needed
                self.memory.record_interaction(user_message, result.get("response", ""))

            return result

        except Exception as exc:
            logger.error("Error during JarvisCore handling: %s", str(exc), exc_info=True)
            return {
                "success": False,
                "intent": "ERROR",
                "action": "CORE_EXCEPTION",
                "response": "An unexpected error occurred while processing your request. Please try again.",
                "data": {"error": str(exc)},
                "toolUsed": "none",
                "memoryUpdated": False,
            }
