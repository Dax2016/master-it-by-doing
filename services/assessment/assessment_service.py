from typing import Any

from services.assessment.bedrock_evaluator import BedrockEvaluator
from services.assessment.ground_truth import GroundTruthEvaluator


class AssessmentService:
    """Coordinate AI evidence collection and deterministic validation."""

    def __init__(
        self,
        bedrock_evaluator: BedrockEvaluator | None = None,
        ground_truth_evaluator: GroundTruthEvaluator | None = None,
    ) -> None:
        self.bedrock_evaluator = (
            bedrock_evaluator or BedrockEvaluator()
        )
        self.ground_truth_evaluator = (
            ground_truth_evaluator or GroundTruthEvaluator()
        )

    def evaluate(
        self,
        mission: dict[str, Any],
        attempt: dict[str, Any],
    ) -> dict[str, Any]:
        """Evaluate an attempt and return the authoritative result."""

        mission_with_criteria = {
            **mission,
            "criteria": (
                self.ground_truth_evaluator.get_required_criteria(
                    mission
                )
            ),
        }

        # ---------------------------------------------------------------
        # AI evidence collection.
        # ---------------------------------------------------------------

        bedrock_evaluation = self.bedrock_evaluator.evaluate(
            mission=mission_with_criteria,
            attempt=attempt,
        )

        # ---------------------------------------------------------------
        # Normalize AI criteria so Ground Truth can validate them
        # against authoritative criterion IDs.
        # ---------------------------------------------------------------

        bedrock_evaluation = self._normalize_criteria(
            bedrock_evaluation,
            mission_with_criteria["criteria"],
        )

        # ---------------------------------------------------------------
        # Deterministic validation.
        #
        # Ground Truth owns:
        #   - passed
        #   - score
        #   - status
        #   - criterion results
        #
        # Bedrock provides:
        #   - evidence
        #   - strengths
        #   - weaknesses
        #   - feedback
        # ---------------------------------------------------------------

        ground_truth_result = self.ground_truth_evaluator.evaluate(
            mission=mission,
            evaluation=bedrock_evaluation,
        )

        # ---------------------------------------------------------------
        # Return the authoritative evaluation.
        #
        # Do NOT expose Bedrock's next_action as the authoritative
        # learning progression decision. Adaptive progression is owned
        # by adapt_learning_mission().
        # ---------------------------------------------------------------

        return {
            **ground_truth_result,
            "strengths": bedrock_evaluation["strengths"],
            "weaknesses": bedrock_evaluation["weaknesses"],
            "feedback": bedrock_evaluation["feedback"],
        }

    @staticmethod
    def _normalize_criteria(
        evaluation: dict[str, Any],
        required_criteria: list[dict[str, str]],
    ) -> dict[str, Any]:
        """Attach authoritative IDs when the model omits them."""

        criteria = evaluation.get("criteria")

        if not isinstance(criteria, list):
            return evaluation

        normalized = []

        for index, criterion in enumerate(criteria):
            if not isinstance(criterion, dict):
                normalized.append(criterion)
                continue

            enriched = dict(criterion)
            criterion_id = enriched.get("id")

            # -----------------------------------------------------------
            # Prefer an exact criterion-name match.
            # -----------------------------------------------------------

            if not criterion_id:
                criterion_name = str(
                    enriched.get("name", "")
                ).strip().lower()

                for required in required_criteria:
                    if (
                        required["name"].strip().lower()
                        == criterion_name
                    ):
                        criterion_id = required["id"]
                        break

            # -----------------------------------------------------------
            # Bedrock is instructed to preserve criterion order.
            # Only use positional matching when the complete list
            # was returned.
            # -----------------------------------------------------------

            if (
                not criterion_id
                and len(criteria) == len(required_criteria)
                and index < len(required_criteria)
            ):
                criterion_id = required_criteria[index]["id"]

            if criterion_id:
                enriched["id"] = criterion_id

            normalized.append(enriched)

        return {
            **evaluation,
            "criteria": normalized,
        }
