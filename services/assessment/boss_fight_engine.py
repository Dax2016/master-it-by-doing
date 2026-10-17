from copy import deepcopy
from datetime import datetime, timezone
import uuid
from typing import Any


class BossFightEngine:
    """Manage independent, learner-scoped practical challenges."""

    VALID_STATUSES = {"ready", "in_progress", "passed", "failed"}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _skill_key(skill: str) -> str:
        return str(skill).strip().casefold().replace("_", "-").replace(" ", "-")

    def create_challenge(
        self,
        learner: Any,
        skill: str,
        parent_mission_id: str,
        parent_mission_title: str | None = None,
        challenge_brief: dict | None = None,
    ) -> dict:
        if not str(skill).strip():
            raise ValueError("Skill is required.")
        if not str(parent_mission_id).strip():
            raise ValueError("Parent mission ID is required.")

        challenge = {
            "id": f"boss-{uuid.uuid4().hex}",
            "learner_id": learner.learner_id,
            "skill": str(skill).strip(),
            "parent_mission_id": str(parent_mission_id).strip(),
            "parent_mission_title": parent_mission_title,
            "challenge_brief": deepcopy(challenge_brief or {}),
            "status": "ready",
            "created_at": self._now(),
            "started_at": None,
            "completed_at": None,
            "evaluation": None,
        }
        learner.boss_fights.append(challenge)
        return deepcopy(challenge)

    def _find(
        self,
        learner: Any,
        challenge_id: str,
        skill: str,
        parent_mission_id: str,
    ) -> dict:
        if not str(skill).strip() or not str(parent_mission_id).strip():
            raise ValueError("Skill and parent mission ID are required.")

        challenge = next(
            (
                item for item in learner.boss_fights
                if item.get("id") == challenge_id
            ),
            None,
        )
        if challenge is None:
            raise ValueError("Boss Fight not found for this learner.")

        if challenge.get("learner_id") != learner.learner_id:
            raise ValueError("Boss Fight belongs to another learner.")

        if self._skill_key(challenge.get("skill", "")) != self._skill_key(skill):
            raise ValueError("Skill does not match this Boss Fight.")

        if challenge.get("parent_mission_id") != str(parent_mission_id).strip():
            raise ValueError("Parent mission does not match this Boss Fight.")

        if challenge.get("status") not in self.VALID_STATUSES:
            raise ValueError("Boss Fight has an invalid stored status.")

        return challenge

    def get_challenge(
        self,
        learner: Any,
        challenge_id: str,
        *,
        skill: str,
        parent_mission_id: str,
    ) -> dict:
        return deepcopy(
            self._find(learner, challenge_id, skill, parent_mission_id)
        )

    def start_challenge(
        self,
        learner: Any,
        challenge_id: str,
        *,
        skill: str,
        parent_mission_id: str,
    ) -> dict:
        challenge = self._find(
            learner, challenge_id, skill, parent_mission_id
        )
        if challenge["status"] != "ready":
            raise ValueError(
                f"Cannot start a Boss Fight in state '{challenge['status']}'."
            )

        challenge["status"] = "in_progress"
        challenge["started_at"] = self._now()
        return deepcopy(challenge)

    def append_interview_exchange(
        self,
        learner: Any,
        challenge_id: str,
        *,
        skill: str,
        parent_mission_id: str,
        learner_response: str = "",
        attempt_type: str = "text",
        examiner_response: str,
    ) -> dict:
        """Append an interview exchange without finalizing the challenge."""
        challenge = self._find(
            learner, challenge_id, skill, parent_mission_id
        )
        if challenge["status"] != "in_progress":
            raise ValueError(
                "Interview turns require an in-progress Boss Fight."
            )
        if attempt_type not in {"code", "text", "answer"}:
            raise ValueError("attempt_type must be code, text, or answer.")
        if not isinstance(examiner_response, str) or not examiner_response.strip():
            raise ValueError("An examiner response is required.")

        transcript = challenge.setdefault("interview_transcript", [])
        response = learner_response.strip() if isinstance(
            learner_response, str
        ) else ""

        if response:
            transcript.append({
                "role": "learner",
                "content": response[:12000],
                "attempt_type": attempt_type,
                "timestamp": self._now(),
            })

        transcript.append({
            "role": "examiner",
            "content": examiner_response.strip()[:4000],
            "timestamp": self._now(),
        })
        return deepcopy(challenge)

    def record_evaluation(
        self,
        learner: Any,
        challenge_id: str,
        *,
        skill: str,
        parent_mission_id: str,
        evaluation: dict,
    ) -> dict:
        challenge = self._find(
            learner, challenge_id, skill, parent_mission_id
        )
        if challenge["status"] != "in_progress":
            raise ValueError(
                "Only an in-progress Boss Fight can be evaluated."
            )

        if not isinstance(evaluation, dict):
            raise ValueError("A valid evaluation object is required.")

        if evaluation.get("status") != "evaluated":
            raise ValueError("Evaluation must have status 'evaluated'.")

        if evaluation.get("learner_id") != learner.learner_id:
            raise ValueError("Evaluation learner does not match the challenge.")

        if self._skill_key(evaluation.get("skill", "")) != self._skill_key(skill):
            raise ValueError("Evaluation skill does not match the challenge.")

        if evaluation.get("mission_id") != challenge["parent_mission_id"]:
            raise ValueError("Evaluation mission does not match the parent mission.")

        passed = evaluation.get("passed")
        score = evaluation.get("score")
        passed_criteria = evaluation.get("passed_criteria")
        total_criteria = evaluation.get("total_criteria")

        if not isinstance(passed, bool):
            raise ValueError("Evaluation must contain a boolean 'passed' result.")

        if (
            isinstance(score, bool)
            or not isinstance(score, (int, float))
            or not 0 <= score <= 100
        ):
            raise ValueError("Evaluation score must be between 0 and 100.")

        if (
            isinstance(passed_criteria, bool)
            or not isinstance(passed_criteria, int)
            or isinstance(total_criteria, bool)
            or not isinstance(total_criteria, int)
            or total_criteria <= 0
            or not 0 <= passed_criteria <= total_criteria
        ):
            raise ValueError("Evaluation criteria counts are invalid.")

        if passed != (passed_criteria == total_criteria):
            raise ValueError(
                "Evaluation pass result conflicts with its criteria counts."
            )

        # Preserve the assessment result. Do not complete or advance the
        # parent mission here; mission progression is a separate operation.
        challenge["evaluation"] = deepcopy(evaluation)
        challenge["status"] = "passed" if passed else "failed"
        challenge["completed_at"] = self._now()

        return deepcopy(challenge)
