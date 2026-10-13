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
    active_mission: dict[str, Any] | None = None
    active_practice: dict[str, Any] | None = None
    active_missions: dict[str, dict[str, Any]] = field(default_factory=dict)
    active_practices: dict[str, dict[str, Any]] = field(default_factory=dict)
    boss_fights: list[dict[str, Any]] = field(default_factory=list)

    goals: list[dict] = field(default_factory=list)
    completed_missions: list[dict] = field(default_factory=list)
    attempts: list[dict] = field(default_factory=list)

    evidence: list[dict] = field(default_factory=list)
    capabilities: list[dict] = field(default_factory=list)

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

    def add_evidence(self, evidence: dict) -> None:
        """Record evidence produced by an evaluated attempt."""
        self.evidence.append(evidence)

    def add_capability(self, capability: dict) -> None:
        """Record or update a demonstrated learner capability."""

        learner_id = capability.get("learner_id")
        mission_id = capability.get("mission_id")

        for existing in self.capabilities:
            if (
                existing.get("learner_id") == learner_id
                and existing.get("mission_id") == mission_id
            ):
                existing_evidence = existing.setdefault(
                    "evidence_ids",
                    [],
                )

                for evidence_id in capability.get(
                    "evidence_ids",
                    [],
                ):
                    if evidence_id not in existing_evidence:
                        existing_evidence.append(evidence_id)

                existing_criteria = existing.setdefault(
                    "demonstrated_criteria",
                    [],
                )

                for criterion in capability.get(
                    "demonstrated_criteria",
                    [],
                ):
                    criterion_id = criterion.get("id")

                    if not criterion_id:
                        if criterion not in existing_criteria:
                            existing_criteria.append(criterion)
                        continue

                    existing_index = next(
                        (
                            index
                            for index, existing_criterion in enumerate(
                                existing_criteria
                            )
                            if existing_criterion.get("id") == criterion_id
                        ),
                        None,
                    )

                    if existing_index is None:
                        existing_criteria.append(criterion)
                    else:
                        existing_criteria[existing_index] = criterion

                existing["attempts"] = existing.get(
                    "attempts",
                    1,
                ) + 1

                new_score = capability.get(
                    "score",
                    existing.get("score", 0),
                )

                existing["score"] = new_score
                existing["best_score"] = max(
                    existing.get(
                        "best_score",
                        existing.get("score", 0),
                    ),
                    new_score,
                )

                return

        capability["attempts"] = capability.get(
            "attempts",
            1,
        )
        capability["best_score"] = capability.get(
            "score",
            0,
        )

        self.capabilities.append(capability)

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

    @staticmethod
    def _skill_key(skill: str | None) -> str:
        """Normalize skill names so equivalent labels share one state key."""
        return str(skill or "").strip().casefold().replace("_", "-").replace(" ", "-")

    def get_active_mission(self, skill: str | None = None) -> dict[str, Any] | None:
        """Return the active mission for a skill, with legacy fallback."""
        if skill is None:
            return self.active_mission

        key = self._skill_key(skill)
        mission = self.active_missions.get(key)
        if mission is not None:
            return mission

        if (
            self.active_mission
            and self._skill_key(self.active_mission.get("skill")) == key
        ):
            return self.active_mission
        return None

    def set_active_mission(self, mission: dict[str, Any], skill: str | None = None) -> None:
        resolved_skill = mission.get("skill") or skill
        active = {
            "mission_id": mission.get("id") or mission.get("mission_id"),
            "title": mission.get("title"),
            "description": mission.get("description"),
            "skill": resolved_skill,
            "status": "in_progress",
        }
        key = self._skill_key(resolved_skill)
        if key:
            self.active_missions[key] = active
        self.active_mission = active

    def clear_active_mission(self, skill: str | None = None) -> None:
        """Clear one skill's mission, or all missions for legacy callers."""
        if skill is None:
            self.active_missions.clear()
            self.active_mission = None
            return

        key = self._skill_key(skill)
        self.active_missions.pop(key, None)
        if (
            self.active_mission
            and self._skill_key(self.active_mission.get("skill")) == key
        ):
            self.active_mission = next(
                reversed(self.active_missions.values()), None
            )

    def get_active_practice(self, skill: str | None = None) -> dict[str, Any] | None:
        """Return the active targeted exercise for a skill."""
        if skill is None:
            return self.active_practice

        key = self._skill_key(skill)
        practice = self.active_practices.get(key)
        if practice is not None:
            return practice

        if (
            self.active_practice
            and self._skill_key(self.active_practice.get("skill")) == key
        ):
            return self.active_practice
        return None

    def set_active_practice(
        self, practice: dict[str, Any], skill: str | None = None
    ) -> None:
        """Persist targeted practice while preserving the legacy field."""
        resolved_skill = practice.get("skill") or skill
        if resolved_skill:
            self.active_practices[self._skill_key(resolved_skill)] = practice
        self.active_practice = practice

    def clear_active_practice(self, skill: str | None = None) -> None:
        """Clear one skill's practice, or all practice for legacy callers."""
        if skill is None:
            self.active_practices.clear()
            self.active_practice = None
            return

        key = self._skill_key(skill)
        self.active_practices.pop(key, None)
        if (
            self.active_practice
            and self._skill_key(self.active_practice.get("skill")) == key
        ):
            self.active_practice = next(
                reversed(self.active_practices.values()), None
            )

    def to_dict(self) -> dict:
        """Return the learner state as a serializable dictionary."""
        return {
            "learner_id": self.learner_id,
            "active_mission": self.active_mission,
            "active_practice": self.active_practice,
            "active_missions": self.active_missions,
            "active_practices": self.active_practices,
            "boss_fights": self.boss_fights,
            "goals": self.goals,
            "completed_missions": self.completed_missions,
            "attempts": self.attempts,
            "evidence": self.evidence,
            "capabilities": self.capabilities,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "mastery": self.mastery,
        }
    def get_capability_profile(self) -> list[dict]:
        """
        Aggregate demonstrated capabilities across missions by skill.
        """

        profiles: dict[str, dict] = {}

        for capability in self.capabilities:
            skill = str(capability.get("skill", "")).strip()

            if not skill:
                continue

            if skill not in profiles:
                profiles[skill] = {
                    "skill": skill,
                    "missions": 0,
                    "attempts": 0,
                    "evidence_ids": [],
                    "concept_ids": [],
                    "best_score": 0,
                    "demonstrated_criteria": [],
                }

            profile = profiles[skill]

            profile["missions"] += 1
            profile["attempts"] += capability.get(
                "attempts",
                1,
            )

            for evidence_id in capability.get(
                "evidence_ids",
                [],
            ):
                if evidence_id not in profile["evidence_ids"]:
                    profile["evidence_ids"].append(evidence_id)

            for concept_id in capability.get(
                "concept_ids",
                [],
            ):
                if concept_id not in profile["concept_ids"]:
                    profile["concept_ids"].append(concept_id)

            profile["best_score"] = max(
                profile["best_score"],
                capability.get(
                    "best_score",
                    capability.get("score", 0),
                ),
            )

            existing_criteria = profile["demonstrated_criteria"]

            for criterion in capability.get(
                "demonstrated_criteria",
                [],
            ):
                criterion_id = criterion.get("id")

                if not criterion_id:
                    if criterion not in existing_criteria:
                        existing_criteria.append(criterion)
                    continue

                existing_index = next(
                    (
                        index
                        for index, existing_criterion in enumerate(
                            existing_criteria
                        )
                        if existing_criterion.get("id") == criterion_id
                    ),
                    None,
                )

                if existing_index is None:
                    existing_criteria.append(criterion)
                else:
                    existing_criteria[existing_index] = criterion

        return list(profiles.values())

    def get_learner_profile(
        self,
        skill: str | None = None,
        learner_level: str | None = None,
    ) -> dict:
        """Return a read-only profile, optionally scoped to one skill."""

        def normalize(value: Any) -> str:
            return (
                str(value or "")
                .strip()
                .casefold()
                .replace("_", "-")
                .replace(" ", "-")
            )

        current_goal = None
        for goal in reversed(self.goals):
            if skill is not None and normalize(goal.get("skill")) != normalize(skill):
                continue
            if (
                learner_level is not None
                and normalize(goal.get("learner_level")) != normalize(learner_level)
            ):
                continue
            current_goal = goal
            break

        active_mission = (
            self.get_active_mission(skill)
            if skill is not None
            else self.active_mission
        )

        mastered = []
        developing = []
        needs_practice = []

        for stored_skill, missions in self.mastery.items():
            for mission, mastery in missions.items():
                entry = {
                    "skill": stored_skill,
                    "mission": mission,
                    **mastery,
                }

                status = mastery.get("status")
                if status == "mastered":
                    mastered.append(entry)
                elif status == "needs_practice":
                    needs_practice.append(entry)
                elif status == "developing":
                    developing.append(entry)

        return {
            "learner_id": self.learner_id,
            "current": {
                "goal": current_goal,
                "active_mission": active_mission,
                "active_missions": self.active_missions,
                "active_practices": self.active_practices,
            },
            "demonstrated": {
                "capabilities": self.get_capability_profile(),
                "completed_missions": self.completed_missions,
                "evidence_count": len(self.evidence),
            },
            "mastery": {
                "mastered": mastered,
                "developing": developing,
                "needs_practice": needs_practice,
            },
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "next": {"mission": None},
        }
