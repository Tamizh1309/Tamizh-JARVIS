import re
import json
import logging
from typing import Dict, Any, Optional
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager
from ai.provider import AIProvider

logger = logging.getLogger("tamizh_jarvis.tools.profile")


class ProfileTool(BaseTool):
    """Tool for managing user profile, active career objectives, personalized placement roadmap, and resume analysis."""

    def __init__(self, memory_manager: MemoryManager, ai_provider: Optional[AIProvider] = None):
        self.memory = memory_manager
        self.ai = ai_provider

    @property
    def name(self) -> str:
        return "profile_tool"

    @property
    def description(self) -> str:
        return "Manages and retrieves user profile, active career objectives, study targets, and analyzes resumes."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action_raw = params.get("action", "get_career_goal")
        action = action_raw.lower().strip() if isinstance(action_raw, str) else "get_career_goal"
        profile = self.memory.profile.get_profile()

        # 1. SET / UPDATE CAREER GOAL
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
            await self.memory.create("GOAL", "primary_goal", new_goal)
            data = {
                "primary_goal": new_goal,
                "user_name": profile.name,
            }
            return self.format_output(
                success=True,
                action="goal_updated",
                data=data,
                message=f"Career goal successfully updated to: '{new_goal}'."
            )

        # 2. GET CAREER GOAL (Real stored value from SQLite)
        if action in ["get_career_goal", "get_goal", "career_goal"]:
            data = {
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "target_daily_study_hours": profile.target_daily_study_hours,
                "subjects": profile.current_subjects,
                "weak_topics": profile.weak_topics,
            }
            return self.format_output(
                success=True,
                action="career_goal",
                data=data,
                message=f"Your primary career goal is: {profile.primary_goal}. Daily target is {profile.target_daily_study_hours} hours."
            )

        # 3. PLACEMENT ROADMAP (Personalized to user's primary goal and weak topics)
        if action in ["placement", "campus_placement", "placement_prep"]:
            goal = profile.primary_goal
            weak_topics = profile.weak_topics

            if "gate" in goal.lower():
                strategy = (
                    f"GATE CS Placement & PSU Roadmap for {profile.name}:\n"
                    f"1. Target Goal: {goal}\n"
                    f"2. Core Subjects: {', '.join(profile.current_subjects[:4])}\n"
                    f"3. High-Priority Weak Topics: {', '.join(weak_topics)}\n"
                    "4. Preparation Focus: Practice 15-20 Previous Year Questions (PYQs) daily under timed conditions."
                )
            else:
                strategy = (
                    f"Software Engineering Placement Strategy for {profile.name}:\n"
                    f"1. Career Focus: {goal}\n"
                    f"2. Coding Competency: Master 75 core LeetCode patterns (focusing especially on {', '.join(weak_topics)})\n"
                    f"3. System Design: Scalability, Redis caching, database indexing, and microservices\n"
                    f"4. Core CS: Revise Operating Systems (Paging/Deadlocks) and DBMS (ACID & Transactions)"
                )

            data = {
                "user_name": profile.name,
                "primary_goal": goal,
                "weak_topics": weak_topics,
                "recommendation": strategy
            }
            return self.format_output(
                success=True,
                action="placement",
                data=data,
                message=strategy
            )

        # 4. INTERVIEW PREPARATION (Personalized to user's profile)
        if action in ["interview", "mock_interview"]:
            goal = profile.primary_goal
            weak = profile.weak_topics

            questions = [
                f"How would you optimize queries on high-throughput database tables given your goal in {goal}?",
                f"Explain how you would handle race conditions in {weak[0] if weak else 'concurrency'}.",
                "Walk me through the time and space trade-offs of a recent problem you solved."
            ]

            strategy = (
                f"Personalized Technical Interview Preparation for {profile.name}:\n"
                f"Target Goal: {goal}\n\n"
                "Targeted Technical Questions:\n" +
                "\n".join([f"- {q}" for q in questions]) +
                "\n\nKey Checklist: Verbalize trade-offs out loud, test edge cases (empty/null inputs), and analyze complexity before coding."
            )

            data = {
                "user_name": profile.name,
                "primary_goal": goal,
                "sample_questions": questions,
                "recommendation": strategy
            }
            return self.format_output(
                success=True,
                action="interview",
                data=data,
                message=strategy
            )

        # 5. RESUME REVIEW (Real analysis of user-supplied resume content)
        if action in ["resume", "cv", "resume_review", "analyze_resume"]:
            resume_text = params.get("resume_text")

            if not resume_text or len(resume_text.strip()) < 10:
                return self.format_output(
                    success=True,
                    action="resume",
                    data={"resume_provided": False},
                    message=(
                        "No resume content was provided to analyze. Please provide your resume content "
                        "(e.g., 'Review my resume: [paste text or bullet points]').\n\n"
                        "Resume Guidelines to Prepare:\n"
                        f"1. Target Alignment: Align skills and project headings with your target goal: '{profile.primary_goal}'.\n"
                        "2. Quantify Achievements: Include metrics (e.g., '% latency reduced', 'users served').\n"
                        "3. Active Verbs: Start bullet points with strong technical verbs: Architected, Implemented, Benchmarked."
                    )
                )

            # User provided actual resume content - analyze it
            if self.ai and getattr(self.ai, "name", "") != "fallback":
                try:
                    ai_prompt = (
                        f"User Career Goal: {profile.primary_goal}\n"
                        f"Resume Content:\n```\n{resume_text}\n```\n\n"
                        "Perform an ATS-focused resume analysis. Return strictly JSON with keys: "
                        "ats_score (integer 1-100), missing_information (list of strings), "
                        "vague_bullets (list of strings), suggested_improvements (list of strings), "
                        "strengths (list of strings)."
                    )
                    ai_res = await self.ai.generate(prompt=ai_prompt, json_mode=True)
                    parsed = json.loads(ai_res)
                    data = {
                        "resume_provided": True,
                        "ats_score": parsed.get("ats_score", 75),
                        "missing_information": parsed.get("missing_information", []),
                        "vague_bullets": parsed.get("vague_bullets", []),
                        "suggested_improvements": parsed.get("suggested_improvements", []),
                        "strengths": parsed.get("strengths", []),
                    }
                    msg = (
                        f"Resume Analysis for {profile.primary_goal} (ATS Score: {data['ats_score']}/100):\n"
                        f"Strengths: {', '.join(data['strengths'][:2])}.\n"
                        f"Improvements: {', '.join(data['suggested_improvements'][:2])}."
                    )
                    return self.format_output(success=True, action="resume", data=data, message=msg)
                except Exception as e:
                    logger.warning("AI resume analysis fallback: %s", str(e))

            # Deterministic Resume Analysis
            metrics_found = re.findall(r"(\d+%\s*|\$\d+|\d+\s*(?:ms|users|requests|qps|x))", resume_text, re.IGNORECASE)
            action_verbs = ["architected", "developed", "implemented", "optimized", "built", "engineered", "designed", "deployed"]
            found_verbs = [v for v in action_verbs if re.search(r"\b" + v + r"\b", resume_text, re.IGNORECASE)]

            suggestions = []
            if len(metrics_found) < 2:
                suggestions.append("Add measurable metrics to project bullets (e.g. 'reduced latency by 35%', 'scaled to 1,000+ users').")
            if len(found_verbs) < 3:
                suggestions.append("Lead bullet points with active verbs: Architected, Spearheaded, Optimized, Benchmarked.")
            if profile.primary_goal.lower() not in resume_text.lower():
                suggestions.append(f"Tailor summary and skills directly to your primary target: '{profile.primary_goal}'.")

            score = min(95, 60 + len(metrics_found) * 5 + len(found_verbs) * 4)

            data = {
                "resume_provided": True,
                "ats_score": score,
                "metrics_detected": metrics_found,
                "action_verbs_detected": found_verbs,
                "suggested_improvements": suggestions or ["Resume structure is strong. Continue highlighting impact."],
            }
            msg = f"Resume Analysis for {profile.primary_goal} (ATS Score: {score}/100). Found {len(metrics_found)} metrics and {len(found_verbs)} active verbs."
            return self.format_output(success=True, action="resume", data=data, message=msg)

        # DEFAULT: GET PROFILE
        profile_dict = profile.model_dump()
        return self.format_output(
            success=True,
            action="user_profile",
            data={"profile": profile_dict},
            message=f"User profile loaded for {profile.name}."
        )
