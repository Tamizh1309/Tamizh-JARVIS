from typing import Dict, Any
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class ProfileTool(BaseTool):
    """Tool for querying and updating user profile, preferences, and career goals."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "profile_tool"

    @property
    def description(self) -> str:
        return "Manages and retrieves user profile, active career objectives, and study targets."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action_raw = params.get("action", "get_career_goal")
        action = action_raw.lower().strip() if isinstance(action_raw, str) else "get_career_goal"

        # SET / UPDATE CAREER GOAL
        if action in ["set_goal", "set_career_goal", "update_goal"]:
            new_goal = params.get("goal")
            if not new_goal:
                return self.format_output(
                    success=False,
                    action="set_career_goal",
                    data={"error": "Goal text is required."},
                    message="Career goal update failed: Goal text is required."
                )
            await self.memory.profile.set_goal(new_goal)
            data = {
                "primary_goal": new_goal,
                "user_name": self.memory.profile.get_profile().name,
            }
            return self.format_output(
                success=True,
                action="goal_updated",
                data=data,
                message=f"Career goal successfully updated to: '{new_goal}'."
            )

        # GET CAREER GOAL
        if action in ["get_career_goal", "get_goal", "career_goal"]:
            profile = self.memory.profile.get_profile()
            data = {
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "target_daily_study_hours": profile.target_daily_study_hours,
                "subjects": profile.current_subjects,
            }
            return self.format_output(
                success=True,
                action="career_goal",
                data=data,
                message=f"Your primary career goal is: {profile.primary_goal} (Target study: {profile.target_daily_study_hours} hrs/day)."
            )

        # PLACEMENT PREPARATION
        if action in ["placement", "campus_placement"]:
            profile = self.memory.profile.get_profile()
            rec_lines = [
                f"Campus Placement Roadmap for {profile.name}:",
                "1. Data Structures & Algorithms: Target Top 100 Liked LeetCode questions (Two Pointers, Sliding Window, DP).",
                "2. Core CS Fundamentals: Revise DBMS (Indexing & Normalization), OS (Concurrency & Paging), and CN (TCP/IP).",
                "3. System Design: Review microservices, load balancing, caching (Redis), and SQL vs NoSQL trade-offs.",
                "4. Behavioral: Prepare STAR format responses for project leadership and conflict resolution."
            ]
            recommendation = "\n".join(rec_lines)
            data = {
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "recommendation": recommendation,
                "focus_areas": ["DSA Mastery", "Core CS Fundamentals", "System Design", "Mock Interviews"]
            }
            return self.format_output(
                success=True,
                action="placement",
                data=data,
                message=recommendation
            )

        # INTERVIEW PREPARATION
        if action in ["interview", "mock_interview"]:
            profile = self.memory.profile.get_profile()
            rec_lines = [
                f"Technical Interview Preparation Checklist for {profile.name}:",
                "1. Coding Rounds: Practice explaining time/space complexities out loud before coding.",
                "2. Core CS Rounds: Be ready to write raw SQL queries, explain ACID transactions, and OS deadlocks.",
                "3. Live Debugging: Familiarize yourself with breakpoint debugging and tracing edge cases (null/empty inputs).",
                "4. Questions for Interviewer: Prepare 2 insightful questions about team architecture and engineering standards."
            ]
            recommendation = "\n".join(rec_lines)
            data = {
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "recommendation": recommendation,
                "checklist": [
                    "Verbalize thought process during problem solving",
                    "Analyze time/space complexity before coding",
                    "Handle edge cases and boundary conditions",
                    "Prepare questions about system architecture"
                ]
            }
            return self.format_output(
                success=True,
                action="interview",
                data=data,
                message=recommendation
            )

        # RESUME & CV
        if action in ["resume", "cv", "resume_review"]:
            profile = self.memory.profile.get_profile()
            rec_lines = [
                f"Resume Optimization Guidance for {profile.name}:",
                "1. Quantify Impact: Replace vague descriptions with metrics (e.g. 'Optimized query latency by 45% using composite indexes').",
                "2. Action Verbs: Lead bullet points with strong technical verbs: Architected, Spearheaded, Implemented, Benchmarked.",
                f"3. Technical Stack Alignment: Match your skills section to target role ({profile.primary_goal}).",
                "4. ATS Friendliness: Keep clean single-column formatting without tables or graphic bars."
            ]
            recommendation = "\n".join(rec_lines)
            data = {
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "recommendation": recommendation,
                "ats_tips": [
                    "Single column clean layout",
                    "Lead bullet points with active verbs",
                    "Highlight measurable business & engineering metrics",
                    "Keep length to 1 page for entry/mid-level"
                ]
            }
            return self.format_output(
                success=True,
                action="resume",
                data=data,
                message=recommendation
            )

        # DEFAULT: GET FULL PROFILE
        profile = self.memory.profile.get_profile()
        profile_dict = profile.model_dump()
        return self.format_output(
            success=True,
            action="user_profile",
            data={"profile": profile_dict},
            message=f"User profile loaded for {profile.name}."
        )
