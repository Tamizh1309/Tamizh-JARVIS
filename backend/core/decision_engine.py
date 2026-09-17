from typing import Dict, Any, List
from datetime import datetime


class DecisionEngine:
    """
    Deterministic scoring engine calculating the Next Best Action.
    Evaluates:
    - current time
    - available time
    - pending tasks
    - deadlines
    - goal priority
    - weak topics
    - revision due
    - recent performance
    - unfinished tasks
    - study history
    """

    @staticmethod
    def compute_next_best_action(context: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now()
        current_hour = now.hour
        available_time = context.get("available_time", 45)
        pending_tasks = context.get("pending_tasks", [])
        weak_topics = context.get("weak_topics", [])
        today_mins = context.get("today_study_minutes", 0)
        target_hours = context.get("target_hours", 3.5)
        goal = (context.get("goal") or "").lower()
        study_history = context.get("study_history", [])

        candidates: List[Dict[str, Any]] = []

        # Candidate 1: High Priority / Deadline Tasks
        high_priority_tasks = [t for t in pending_tasks if t.get("priority") == "HIGH" and t.get("status") == "PENDING"]
        if high_priority_tasks:
            top_task = high_priority_tasks[0]
            candidates.append({
                "score": 95,
                "action": "EXECUTE_HIGH_PRIORITY_TASK",
                "title": top_task.get("title", "High Priority Task"),
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": f"Urgent task pending in backlog: '{top_task.get('title')}'. Immediate execution required.",
                "description": top_task.get("description", "Execute pending high priority milestone.")
            })

        # Candidate 2: Weak Topic Spaced Revision
        if weak_topics:
            # Check study history to find least recently studied weak topic
            studied_topics = [s.get("topic", "") for s in study_history]
            selected_topic = weak_topics[0]
            for wt in weak_topics:
                if wt not in studied_topics:
                    selected_topic = wt
                    break

            candidates.append({
                "score": 90,
                "action": "REVISION_SESSION",
                "title": f"Revise {selected_topic}",
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": f"Spaced revision is due for weak topic '{selected_topic}' to maintain retention curve.",
                "description": f"Targeted focus block on {selected_topic} with active recall and PYQ practice."
            })

        # Candidate 3: Evening Review (after 8 PM / 20:00)
        if current_hour >= 20:
            candidates.append({
                "score": 88,
                "action": "DAILY_REVIEW",
                "title": "Evening Review & Next Day Planning",
                "duration_minutes": 20,
                "priority": "MEDIUM",
                "reason": f"Evening slot: Review today's {today_mins} study minutes and organize tomorrow's roadmap.",
                "description": "Consolidate mistakes and confirm priorities for tomorrow."
            })

        # Candidate 4: Goal-Aligned DSA / Coding Practice
        if "software" in goal or "dsa" in goal or "code" in goal:
            candidates.append({
                "score": 85,
                "action": "DSA_PRACTICE",
                "title": "DSA Problem Solving: Two Pointers & Sliding Window",
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": "Continuous daily problem solving directly reinforces your Software Engineering career goal.",
                "description": "Solve 2-3 medium pattern-based problems on LeetCode."
            })

        # Candidate 5: Standard Pending Task
        if pending_tasks:
            next_task = pending_tasks[0]
            candidates.append({
                "score": 75,
                "action": "EXECUTE_TASK",
                "title": next_task.get("title", "Pending Task"),
                "duration_minutes": min(available_time, 30),
                "priority": next_task.get("priority", "MEDIUM"),
                "reason": f"Next pending task in queue: '{next_task.get('title')}'.",
                "description": next_task.get("description", "Execute queued task.")
            })

        # Candidate 6: Core Syllabus Study Block
        candidates.append({
            "score": 70,
            "action": "FOCUS_STUDY",
            "title": "Computer Science Core Subject Mastery",
            "duration_minutes": min(available_time, 45),
            "priority": "MEDIUM",
            "reason": f"Progress toward daily target ({today_mins}m completed of {target_hours}h target).",
            "description": "Focused deep-work session on core theoretical and problem-solving concepts."
        })

        # Sort candidates by score descending and return top recommendation
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = candidates[0]

        return {
            "success": True,
            "action": top["action"],
            "title": top["title"],
            "duration_minutes": top["duration_minutes"],
            "priority": top["priority"],
            "reason": top["reason"],
            "description": top["description"]
        }
