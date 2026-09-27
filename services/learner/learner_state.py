from dataclasses import dataclass, field
from typing import Any


@dataclass
class LearnerState:
    """
    Persistent representation of a learner's learning state.

    This local model is the foundation for the future
    AgentCore Memory integration.
    """

    learner_id: str

    goals: list[dict] = field(default_factory=list)
    completed_missions: list[dict] = field(default_factory=list)
    attempts: list[dict] = field(default_factory=list)

    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)

    mastery: dict[str, dict[str, dict[str, Any]]] = field(
        default_factory=dict
    )

    def add_goal(self, goal: dict) -> None:
        """Record a learning goal."""
        self.goals.append(goal)

    def add_attempt(self, attempt: dict) -> None:
        """Record a learner attempt."""
        self.attempts.append(attempt)

    def add_completed_mission(self, mission: dict) -> None:
        """Record a completed mission."""
        self.completed_missions.append(mission)

    def update_skill_profile(
        self,
        strengths: list[str],
        weaknesses: list[str],
    ) -> None:
        """Update the learner's current strengths and weaknesses."""
        self.strengths = strengths
        self.weaknesses = weaknesses

    def record_mastery(
        self,
        skill: str,
        mission: str,
        status: str,
        score: int,
        passed: bool,
        passed_criteria: int,
        total_criteria: int,
        evidence: dict | None = None,
    ) -> None:
        """
        Persist authoritative mastery evidence for a mission.
        """

        skill_key = str(skill).strip()
        mission_key = str(mission).strip()

        if skill_key not in self.mastery:
            self.mastery[skill_key] = {}

        self.mastery[skill_key][mission_key] = {
            "status": status,
            "score": score,
            "passed": passed,
            "passed_criteria": passed_criteria,
            "total_criteria": total_criteria,
            "evidence": evidence or {},
        }

    def to_dict(self) -> dict:
        """Return the learner state as a serializable dictionary."""
        return {
            "learner_id": self.learner_id,
            "goals": self.goals,
            "completed_missions": self.completed_missions,
            "attempts": self.attempts,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "mastery": self.mastery,
        }