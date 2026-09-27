from typing import Any

from services.assessment.bedrock_evaluator import BedrockEvaluator
from services.assessment.ground_truth import GroundTruthEvaluator
from services.assessment.python_code_validator import PythonCodeValidator


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

        attempt_for_evaluation = dict(attempt)
        syntax_result = None

        if (
            str(attempt.get("attempt_type", "")).strip().lower()
            == "code"
            and str(attempt.get("skill", "")).strip().lower()
            == "python"
        ):
            syntax_result = PythonCodeValidator.validate(
                str(attempt.get("learner_response", "")),
                mission=(
                    mission.get("mission")
                    or mission.get("title")
                    or ""
                ),
            )

            attempt_for_evaluation["validation"] = {
                "python_syntax": syntax_result,
            }

        bedrock_evaluation = self.bedrock_evaluator.evaluate(
            mission=mission_with_criteria,
            attempt=attempt_for_evaluation,
        )

        # ---------------------------------------------------------------
        # Deterministic enforcement.
        #
        # Bedrock may reason about semantic correctness, but it cannot
        # override mechanically verified Python syntax evidence.
        # ---------------------------------------------------------------

        if syntax_result is not None:
            bedrock_evaluation = self._enforce_python_syntax(
                bedrock_evaluation,
                syntax_result,
            )

            # Preserve deterministic validation evidence for Ground Truth.
            bedrock_evaluation["validation"] = {
                "python_syntax": syntax_result,
            }

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
        }

    @staticmethod
    def _enforce_python_syntax(
        evaluation: dict[str, Any],
        syntax_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Prevent AI output from contradicting deterministic syntax evidence."""

        if syntax_result.get("syntax_valid") is True:
            syntax_terms = (
                "syntax error",
                "syntax errors",
                "syntax issue",
                "syntax issues",
                "syntactically invalid",
                "invalid syntax",
                "missing colon",
                "missing quote",
                "unclosed bracket",
                "unclosed parenthesis",
            )

            def contains_syntax_claim(value: Any) -> bool:
                text = str(value).lower()
                return any(term in text for term in syntax_terms)

            cleaned = dict(evaluation)

            cleaned["weaknesses"] = [
                item
                for item in evaluation.get("weaknesses", [])
                if not contains_syntax_claim(item)
            ]

            if contains_syntax_claim(evaluation.get("feedback", "")):
                cleaned["feedback"] = (
                    "The Python submission is syntactically valid. "
                    "Evaluation focuses on the demonstrated mission requirements."
                )

            if contains_syntax_claim(evaluation.get("next_action", "")):
                cleaned["next_action"] = (
                    "Continue improving the mission requirements "
                    "that are not yet demonstrated."
                )

            cleaned["criteria"] = [
                {
                    **criterion,
                    "evidence": (
                        "Python syntax is valid; semantic evidence "
                        "must be evaluated separately."
                        if contains_syntax_claim(
                            criterion.get("evidence", "")
                        )
                        else criterion.get("evidence", "")
                    ),
                }
                for criterion in evaluation.get("criteria", [])
            ]

            return cleaned

        return evaluation

    @staticmethod
    def _normalize_criteria(
        evaluation: dict[str, Any],
        required_criteria: list[dict[str, str]],
    ) -> dict[str, Any]:
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
                    if (
                        required["name"].strip().lower()
                        == criterion_name
                    ):
                        criterion_id = required["id"]
                        break

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
