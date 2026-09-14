import unittest
from typing import Any

from services.assessment.assessment_service import AssessmentService


class FakeBedrockEvaluator:
    def __init__(self) -> None:
        self.mission: dict[str, Any] | None = None

    def evaluate(
        self,
        mission: dict[str, Any],
        attempt: dict[str, Any],
    ) -> dict[str, Any]:
        self.mission = mission
        return {
            "score": 100,
            "passed": True,
            "criteria": [
                {
                    "name": "Prompt user for a guess",
                    "passed": True,
                    "evidence": "input() is used.",
                },
            ],
            "strengths": ["The learner accepts input."],
            "weaknesses": [],
            "feedback": "Good work.",
            "next_action": "Try another mission.",
        }


class OrderedParaphrasedBedrockEvaluator:
    def evaluate(
        self,
        mission: dict[str, Any],
        attempt: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "score": 100,
            "passed": True,
            "criteria": [
                {
                    "name": "Random number is generated",
                    "passed": True,
                    "evidence": "random.randint(1, 10)",
                },
                {
                    "name": "The learner is prompted for input",
                    "passed": True,
                    "evidence": "input()",
                },
                {
                    "name": "The guess is compared with feedback",
                    "passed": True,
                    "evidence": "if guess == number",
                },
                {
                    "name": "The learner can keep guessing",
                    "passed": True,
                    "evidence": "while guess != number",
                },
            ],
            "strengths": [],
            "weaknesses": [],
            "feedback": "Good work.",
            "next_action": "Try another mission.",
        }


class AssessmentServiceTests(unittest.TestCase):
    def test_ground_truth_owns_final_result(self) -> None:
        service = AssessmentService(
            bedrock_evaluator=FakeBedrockEvaluator(),
        )

        result = service.evaluate(
            mission={"skills": ["Prompt user for a guess"]},
            attempt={"submission": "input()"},
        )

        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(result["status"], "mastered")
        self.assertEqual(
            result["feedback"],
            "Good work.",
        )

    def test_forwards_authoritative_criteria_ids(self) -> None:
        bedrock_evaluator = FakeBedrockEvaluator()
        bedrock_evaluator.evaluate = self._paraphrased_evaluation(
            bedrock_evaluator
        )
        service = AssessmentService(
            bedrock_evaluator=bedrock_evaluator,
        )

        result = service.evaluate(
            mission={
                "mission": "Build a Number Guessing Game",
            },
            attempt={"submission": "guess = input()"},
        )

        self.assertIsNotNone(bedrock_evaluator.mission)
        self.assertEqual(
            bedrock_evaluator.mission["criteria"],
            [
                {
                    "id": "random_number",
                    "name": "Generate a random number between 1 and 10",
                },
                {
                    "id": "user_input",
                    "name": "Prompt user for a guess",
                },
                {
                    "id": "feedback",
                    "name": (
                        "Compare guess to the number "
                        "and provide appropriate feedback"
                    ),
                },
                {
                    "id": "multiple_attempts",
                    "name": (
                        "Allow multiple guessing attempts "
                        "until correct"
                    ),
                },
            ],
        )
        self.assertEqual(result["passed_criteria"], 1)
        self.assertEqual(result["total_criteria"], 4)

    def test_normalizes_ordered_paraphrased_criteria(self) -> None:
        service = AssessmentService(
            bedrock_evaluator=OrderedParaphrasedBedrockEvaluator(),
        )

        result = service.evaluate(
            mission={
                "mission": "Build a Number Guessing Game",
            },
            attempt={"submission": "complete game"},
        )

        self.assertEqual(result["score"], 100)
        self.assertTrue(result["passed"])
        self.assertEqual(result["passed_criteria"], 4)

    @staticmethod
    def _paraphrased_evaluation(
        evaluator: FakeBedrockEvaluator,
    ) -> Any:
        def evaluate(
            mission: dict[str, Any],
            attempt: dict[str, Any],
        ) -> dict[str, Any]:
            evaluator.mission = mission
            return {
                "score": 100,
                "passed": True,
                "criteria": [
                    {
                        "id": "user_input",
                        "name": "Reads a guess from the learner",
                        "passed": True,
                        "evidence": "input() is used.",
                    },
                ],
                "strengths": [],
                "weaknesses": [],
                "feedback": "Good work.",
                "next_action": "Try another mission.",
            }

        return evaluate


if __name__ == "__main__":
    unittest.main()