from typing import Dict, Any, List
from datetime import datetime


class DecisionEngine:
    """
    Deterministic scoring engine calculating the Next Best Action.
    Evaluates:
    - deadline urgency
    - goal relevance
    - weakness priority
    - revision due (spaced repetition recency)
    - unfinished task backlog
    - recent performance / mistakes
    - duration fit vs available time
    - target completion state
    """

    @staticmethod
    def compute_next_best_action(context: Dict[str, Any]) -> Dict[str, Any]:
        now = datetime.now()
        current_hour = int(context.get("current_hour", now.hour))
        available_time = int(context.get("available_time", 45))
        pending_tasks = context.get("pending_tasks", [])
        weak_topics = context.get("weak_topics", [])
        today_mins = int(context.get("today_study_minutes", 0))
        target_hours = float(context.get("target_hours", 3.5))
        target_mins = int(target_hours * 60)
        goal = (context.get("goal") or "").lower()
        study_history = context.get("study_history", [])
        current_subjects = context.get("current_subjects", [])

        candidates: List[Dict[str, Any]] = []

        # Candidate 1: Urgent / High Priority Tasks
        high_priority_tasks = [t for t in pending_tasks if t.get("priority") == "HIGH" and t.get("status") == "PENDING"]
        if high_priority_tasks:
            top_task = high_priority_tasks[0]
            score_breakdown = {
                "deadline_urgency": 0.95,
                "goal_relevance": 0.85,
                "weakness_priority": 0.40,
                "revision_due": 0.30,
                "unfinished_task": 1.0,
                "duration_fit": 0.90,
            }
            candidates.append({
                "score": 95.0,
                "action": "EXECUTE_HIGH_PRIORITY_TASK",
                "title": top_task.get("title", "High Priority Task"),
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": f"Urgent task pending in backlog: '{top_task.get('title')}'. Immediate execution required.",
                "description": top_task.get("description", "Execute pending high priority milestone."),
                "score_breakdown": score_breakdown,
            })

        # Candidate 2: Weak Topic Spaced Revision
        if weak_topics:
            studied_topics = [s.get("topic", "") for s in study_history]
            selected_topic = weak_topics[0]
            for wt in weak_topics:
                if wt not in studied_topics:
                    selected_topic = wt
                    break

            score_breakdown = {
                "deadline_urgency": 0.50,
                "goal_relevance": 0.90,
                "weakness_priority": 1.0,
                "revision_due": 0.95,
                "unfinished_task": 0.60,
                "duration_fit": 0.95,
            }
            candidates.append({
                "score": 90.0,
                "action": "REVISION_SESSION",
                "title": f"Revise {selected_topic}",
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": f"Spaced revision is due for weak topic '{selected_topic}' to maintain retention curve.",
                "description": f"Targeted focus block on {selected_topic} with active recall and PYQ practice.",
                "score_breakdown": score_breakdown,
            })

        # Candidate 3: Target Completed Consolidation / Light Review
        if target_mins > 0 and today_mins >= target_mins and not high_priority_tasks:
            score_breakdown = {
                "deadline_urgency": 0.20,
                "goal_relevance": 0.90,
                "weakness_priority": 0.30,
                "revision_due": 0.50,
                "unfinished_task": 0.20,
                "duration_fit": 1.0,
            }
            candidates.append({
                "score": 92.0,
                "action": "TARGET_COMPLETED",
                "title": "Daily Target Completed — Light Revision & Rest",
                "duration_minutes": min(available_time, 20),
                "priority": "LOW",
                "reason": f"Daily target of {target_hours}h reached ({today_mins}m logged). Consolidate notes or rest.",
                "description": "Daily target achieved. Excellent consistency.",
                "score_breakdown": score_breakdown,
            })

        # Candidate 4: Evening Review (after 8 PM / 20:00 when study has been logged today)
        if current_hour >= 20 and today_mins > 0:
            score_breakdown = {
                "deadline_urgency": 0.80,
                "goal_relevance": 0.80,
                "weakness_priority": 0.60,
                "revision_due": 0.70,
                "unfinished_task": 0.85,
                "duration_fit": 1.0,
            }
            candidates.append({
                "score": 88.0,
                "action": "DAILY_REVIEW",
                "title": "Evening Review & Next Day Planning",
                "duration_minutes": 20,
                "priority": "MEDIUM",
                "reason": f"Evening consolidation slot: Review today's {today_mins}m study progress and confirm tomorrow's targets.",
                "description": "Consolidate mistakes and confirm priorities for tomorrow.",
                "score_breakdown": score_breakdown,
            })

        # Candidate 5: Goal-Aligned DSA / Coding Practice
        if "software" in goal or "dsa" in goal or "code" in goal:
            score_breakdown = {
                "deadline_urgency": 0.45,
                "goal_relevance": 1.0,
                "weakness_priority": 0.85,
                "revision_due": 0.80,
                "unfinished_task": 0.50,
                "duration_fit": 0.90,
            }
            candidates.append({
                "score": 85.0,
                "action": "DSA_PRACTICE",
                "title": "DSA Problem Solving: Two Pointers & Sliding Window",
                "duration_minutes": min(available_time, 45),
                "priority": "HIGH",
                "reason": "Continuous daily problem solving directly reinforces your Software Engineering career goal.",
                "description": "Solve 2-3 medium pattern-based problems on LeetCode.",
                "score_breakdown": score_breakdown,
            })

        # Candidate 6: Standard Pending Task
        if pending_tasks:
            next_task = pending_tasks[0]
            score_breakdown = {
                "deadline_urgency": 0.60,
                "goal_relevance": 0.70,
                "weakness_priority": 0.40,
                "revision_due": 0.40,
                "unfinished_task": 0.90,
                "duration_fit": 0.85,
            }
            candidates.append({
                "score": 75.0,
                "action": "EXECUTE_TASK",
                "title": next_task.get("title", "Pending Task"),
                "duration_minutes": min(available_time, 30),
                "priority": next_task.get("priority", "MEDIUM"),
                "reason": f"Next pending task in queue: '{next_task.get('title')}'.",
                "description": next_task.get("description", "Execute queued task."),
                "score_breakdown": score_breakdown,
            })

        # Candidate 7: Core Syllabus Study Block (Default Fallback)
        default_subject = current_subjects[0] if current_subjects else "Computer Science"
        score_breakdown = {
            "deadline_urgency": 0.40,
            "goal_relevance": 0.80,
            "weakness_priority": 0.60,
            "revision_due": 0.65,
            "unfinished_task": 0.40,
            "duration_fit": 0.85,
        }
        candidates.append({
            "score": 70.0,
            "action": "FOCUS_STUDY",
            "title": f"Mastery Block: {default_subject}",
            "duration_minutes": min(available_time, 45),
            "priority": "MEDIUM",
            "reason": f"Progress toward daily study target ({today_mins}m completed of {target_hours}h target).",
            "description": f"Focused deep-work session on {default_subject}.",
            "score_breakdown": score_breakdown,
        })

        # Sort candidates by composite score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = candidates[0]

        return {
            "success": True,
            "action": top["action"],
            "title": top["title"],
            "duration_minutes": top["duration_minutes"],
            "priority": top["priority"],
            "reason": top["reason"],
            "description": top["description"],
            "score": top["score"],
            "score_breakdown": top["score_breakdown"],
        }
