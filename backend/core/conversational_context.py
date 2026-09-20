"""Conversational Context Resolution and Entity Tracking for Tamizh JARVIS."""
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger("tamizh_jarvis.core.conversational_context")


class ConversationalContext:
    """Explicit state container holding active conversation entities."""

    def __init__(self):
        self.active_task: Optional[Dict[str, Any]] = None
        self.active_topic: Optional[str] = None
        self.active_document: Optional[str] = None
        self.active_goal: Optional[str] = None
        self.last_action: Optional[str] = None
        self.last_tool_result: Optional[Dict[str, Any]] = None
        self.turn_history: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_task": self.active_task,
            "active_topic": self.active_topic,
            "active_document": self.active_document,
            "active_goal": self.active_goal,
            "last_action": self.last_action,
            "last_tool_result": self.last_tool_result,
            "conversation_context": self.turn_history[-6:],
        }


class ConversationalContextResolver:
    """Resolves anaphoric and deictic references (it, that, this task, tomorrow, tonight)."""

    def __init__(self):
        self.state = ConversationalContext()

    def update_state_after_execution(
        self,
        intent: str,
        action: str,
        params: Dict[str, Any],
        tool_result: Optional[Dict[str, Any]] = None
    ):
        """Updates active entity state based on the latest successful execution."""
        self.state.last_action = action
        self.state.last_tool_result = tool_result or {}

        # 1. Task Entity Tracking
        if "task" in action.lower() or intent.startswith("TASK_"):
            if tool_result and isinstance(tool_result.get("data"), dict):
                data = tool_result["data"]
                if "id" in data or "title" in data:
                    self.state.active_task = {
                        "id": data.get("id"),
                        "title": data.get("title", params.get("title", "Task")),
                        "priority": data.get("priority", params.get("priority", "MEDIUM")),
                        "status": data.get("status", "PENDING")
                    }
            elif params.get("title"):
                self.state.active_task = {
                    "id": params.get("task_id"),
                    "title": params.get("title"),
                    "priority": params.get("priority", "MEDIUM"),
                    "status": "PENDING"
                }

        # 2. Topic Tracking
        if params.get("topic"):
            self.state.active_topic = params["topic"]
        elif intent in ["STUDY_PLAN", "GATE_REVISION", "MISTAKE_ANALYSIS", "DSA_PRACTICE"]:
            if params.get("subject"):
                self.state.active_topic = params["subject"]

        # 3. Document Tracking
        if params.get("filename"):
            self.state.active_document = params["filename"]
        elif tool_result and isinstance(tool_result.get("data"), dict):
            citations = tool_result["data"].get("citations", [])
            if citations and isinstance(citations, list) and len(citations) > 0:
                first_cit = citations[0]
                if isinstance(first_cit, dict) and first_cit.get("document_name"):
                    self.state.active_document = first_cit["document_name"]

        # 4. Goal Tracking
        if params.get("goal"):
            self.state.active_goal = params["goal"]

    def resolve_references(self, query: str) -> Tuple[str, Dict[str, Any]]:
        """Resolves references in the user message using active entity state."""
        text = query.strip()
        text_lower = text.lower()
        resolved_entities: Dict[str, Any] = {}

        # Temporal Resolution: tomorrow, tonight, later, at 8 PM
        resolved_time = None
        now = datetime.now()
        if "tomorrow" in text_lower:
            target_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
            time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                meridiem = (time_match.group(3) or "am").lower()
                if meridiem == "pm" and hour < 12:
                    hour += 12
                elif meridiem == "am" and hour == 12:
                    hour = 0
                resolved_time = f"{target_date}T{hour:02d}:{minute:02d}:00"
            else:
                resolved_time = f"{target_date}T09:00:00"
            resolved_entities["resolved_due_at"] = resolved_time
            resolved_entities["time_frame"] = "tomorrow"

        elif "tonight" in text_lower or "this evening" in text_lower:
            target_date = now.strftime("%Y-%m-%d")
            time_match = re.search(r"at\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", text_lower)
            if time_match:
                hour = int(time_match.group(1))
                minute = int(time_match.group(2) or 0)
                meridiem = (time_match.group(3) or "pm").lower()
                if meridiem == "pm" and hour < 12:
                    hour += 12
                resolved_time = f"{target_date}T{hour:02d}:{minute:02d}:00"
            else:
                resolved_time = f"{target_date}T20:00:00"
            resolved_entities["resolved_due_at"] = resolved_time
            resolved_entities["time_frame"] = "tonight"

        elif re.search(r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text_lower):
            time_match = re.search(r"\bat\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text_lower)
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3).lower()
            if meridiem == "pm" and hour < 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
            target_date = now.strftime("%Y-%m-%d")
            resolved_time = f"{target_date}T{hour:02d}:{minute:02d}:00"
            resolved_entities["resolved_due_at"] = resolved_time

        # Pronoun & Reference Resolution for Active Task
        is_task_referent = any(
            p in text_lower for p in [
                "make it", "mark it", "set it", "update it", "remind me about it",
                "remind me on that", "do that one", "that task", "this task",
                "the previous one", "that one"
            ]
        ) or text_lower.startswith(("make it ", "do that ", "remind me tomorrow", "remind me tonight"))

        if is_task_referent and self.state.active_task:
            task = self.state.active_task
            resolved_entities["active_task"] = task
            resolved_entities["task_id"] = task.get("id")
            resolved_entities["title"] = task.get("title")

            # Priority modification
            if "high priority" in text_lower or "urgent" in text_lower:
                resolved_entities["priority"] = "HIGH"
                resolved_entities["action"] = "update_task"
                resolved_entities["inferred_intent"] = "TASK_UPDATE"
            elif "medium priority" in text_lower:
                resolved_entities["priority"] = "MEDIUM"
                resolved_entities["action"] = "update_task"
                resolved_entities["inferred_intent"] = "TASK_UPDATE"
            elif "low priority" in text_lower:
                resolved_entities["priority"] = "LOW"
                resolved_entities["action"] = "update_task"
                resolved_entities["inferred_intent"] = "TASK_UPDATE"

            # Reminder modification
            if "remind" in text_lower:
                resolved_entities["action"] = "reminder"
                resolved_entities["inferred_intent"] = "REMINDER"
                resolved_entities["reminder_text"] = f"Reminder for task: {task.get('title')}"
                if resolved_time:
                    resolved_entities["scheduled_for"] = resolved_time

        # Pronoun & Reference Resolution for Active Topic
        if any(p in text_lower for p in ["explain it", "tell me about it", "revise it", "revise that topic", "study it"]):
            if self.state.active_topic:
                resolved_entities["active_topic"] = self.state.active_topic
                resolved_entities["topic"] = self.state.active_topic

        # Pronoun & Reference Resolution for Active Document
        if any(p in text_lower for p in ["that document", "this document", "from my notes", "check my notes"]):
            if self.state.active_document:
                resolved_entities["active_document"] = self.state.active_document

        return text, resolved_entities


_global_context_resolver = None


def get_context_resolver() -> ConversationalContextResolver:
    global _global_context_resolver
    if _global_context_resolver is None:
        _global_context_resolver = ConversationalContextResolver()
    return _global_context_resolver
