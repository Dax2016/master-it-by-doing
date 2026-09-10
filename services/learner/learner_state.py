from dataclasses import dataclass, field


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

    def to_dict(self) -> dict:
        """Return the learner state as a serializable dictionary."""
        return {
            "learner_id": self.learner_id,
            "goals": self.goals,
            "completed_missions": self.completed_missions,
            "attempts": self.attempts,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }