"""Continuous Memory Learning Loop for Tamizh JARVIS."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger("tamizh_jarvis.memory.learning")


class LearningLoop:
    """
    Implements continuous behavioral adaptation and learning:
    Request -> Action -> Result -> Feedback -> Outcome -> Memory.
    """

    def __init__(self, memory_manager):
        self.memory = memory_manager

    @staticmethod
    def _sanitize(metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Ensures no sensitive credentials or keys are persisted."""
        if not metadata:
            return {}
        sanitized = {}
        sensitive_keys = {"token", "secret", "password", "api_key", "authorization", "auth"}
        for k, v in metadata.items():
            if any(sk in k.lower() for sk in sensitive_keys):
                continue
            if isinstance(v, dict):
                sanitized[k] = LearningLoop._sanitize(v)
            elif isinstance(v, (str, int, float, bool, list)):
                sanitized[k] = v
        return sanitized

    async def record_execution(
        self,
        request_text: str,
        intent: str,
        action: str,
        tool: str,
        success: bool,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Records action outcome into structured memory for pattern detection."""
        clean_meta = self._sanitize(metadata)
        hour = datetime.now().hour
        time_slot = "morning" if hour < 12 else ("afternoon" if hour < 17 else "evening")

        record = {
            "timestamp": datetime.now().isoformat(),
            "request": request_text[:120],
            "intent": intent,
            "action": action,
            "tool": tool,
            "success": success,
            "duration_ms": duration_ms,
            "time_slot": time_slot,
            "metadata": clean_meta
        }

        # 1. Store action history log in memory_records
        log_key = f"action_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{action}"
        await self.memory.long_term.create_memory(
            category="LEARNING_LOGS",
            key=log_key,
            value=record
        )

        # 2. Update Tool Usage Frequency
        tool_entry = await self.memory.long_term.read_memory("USER_PREFERENCES", f"tool_freq_{tool}")
        current_tool_count = tool_entry.get("value", {}).get("count", 0) if tool_entry else 0
        await self.memory.long_term.create_memory(
            category="USER_PREFERENCES",
            key=f"tool_freq_{tool}",
            value={"count": current_tool_count + 1, "last_used": datetime.now().isoformat()}
        )

        # 3. Update Success / Failure Counts
        stat_key = f"action_stat_{action}"
        stat_entry = await self.memory.long_term.read_memory("LEARNING_INSIGHTS", stat_key)
        cur_stats = stat_entry.get("value", {"success": 0, "failed": 0}) if stat_entry else {"success": 0, "failed": 0}
        if success:
            cur_stats["success"] = cur_stats.get("success", 0) + 1
        else:
            cur_stats["failed"] = cur_stats.get("failed", 0) + 1
        await self.memory.long_term.create_memory(
            category="LEARNING_INSIGHTS",
            key=stat_key,
            value=cur_stats
        )

        # 4. Track Study / Coding patterns if applicable
        if "study" in action or "gate" in action.lower():
            topic = clean_meta.get("topic") or clean_meta.get("subject")
            if topic:
                pref_key = f"study_focus_{topic.lower()}"
                prev = await self.memory.long_term.read_memory("USER_PREFERENCES", pref_key)
                cnt = prev.get("value", {}).get("count", 0) if prev else 0
                await self.memory.long_term.create_memory(
                    category="USER_PREFERENCES",
                    key=pref_key,
                    value={"topic": topic, "count": cnt + 1, "last_studied": datetime.now().isoformat()}
                )

        if "code" in action or tool == "coding_tool":
            lang = clean_meta.get("language", "python")
            lang_key = f"preferred_lang_{lang.lower()}"
            prev_l = await self.memory.long_term.read_memory("USER_PREFERENCES", lang_key)
            l_cnt = prev_l.get("value", {}).get("count", 0) if prev_l else 0
            await self.memory.long_term.create_memory(
                category="USER_PREFERENCES",
                key=lang_key,
                value={"language": lang, "count": l_cnt + 1}
            )

    async def get_learning_summary(self) -> Dict[str, Any]:
        """Summarizes learned user behaviors and execution statistics."""
        tool_records = await self.memory.long_term.list_memory_by_category("USER_PREFERENCES")
        stat_records = await self.memory.long_term.list_memory_by_category("LEARNING_INSIGHTS")

        most_used_tools = []
        preferences = []
        for r in tool_records:
            k = r.get("key", "")
            if k.startswith("tool_freq_"):
                tool_name = k.replace("tool_freq_", "")
                most_used_tools.append({"tool": tool_name, "count": r.get("value", {}).get("count", 1)})
            elif k.startswith("preferred_lang_") or k.startswith("study_focus_"):
                preferences.append(r.get("value", {}))

        most_used_tools.sort(key=lambda x: x["count"], reverse=True)

        action_stats = {}
        for s in stat_records:
            action_name = s.get("key", "").replace("action_stat_", "")
            action_stats[action_name] = s.get("value", {})

        return {
            "most_used_tools": most_used_tools[:5],
            "preferences": preferences[:10],
            "action_performance": action_stats,
            "total_preference_entries": len(tool_records),
        }
