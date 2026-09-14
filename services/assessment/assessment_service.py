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

        bedrock_evaluation = self.bedrock_evaluator.evaluate(
            mission=mission_with_criteria,
            attempt=attempt,
        )

        bedrock_evaluation = self._normalize_criteria(
            bedrock_evaluation,
            mission_with_criteria["criteria"],
        )

        ground_truth_result = self.ground_truth_evaluator.evaluate(
            mission=mission,
            evaluation=bedrock_evaluation,
        )

        return {
            **ground_truth_result,
            "strengths": bedrock_evaluation["strengths"],
            "weaknesses": bedrock_evaluation["weaknesses"],
            "feedback": bedrock_evaluation["feedback"],
            "next_action": bedrock_evaluation["next_action"],
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

            if not criterion_id:
                criterion_name = str(
                    enriched.get("name", "")
                ).strip().lower()

                for required in required_criteria:
                    if required["name"].strip().lower() == criterion_name:
                        criterion_id = required["id"]
                        break

            # Bedrock is instructed to preserve criterion order. Use that
            # contract only when it returned the complete list.
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