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

def test_valid_python_cannot_be_reported_as_syntax_error():
    service = AssessmentService(
        bedrock_evaluator=FakeBedrockEvaluator(),
    )

    valid_python = '''
questions = [
    {"question": "What keyword defines a function?", "answer": "def"},
    {"question": "What data type stores ordered items?", "answer": "list"},
]

def run_quiz():
    score = 0

    for item in questions:
        print(item["question"])
        answer = input("Your answer: ").strip().lower()

        if answer == item["answer"]:
            print("Correct!")
            score += 1

    print(f"Final score: {score}/{len(questions)}")

run_quiz()
'''

    result = service.evaluate(
        mission={"title": "Build a Command-Line Quiz"},
        attempt={
            "skill": "python",
            "attempt_type": "code",
            "learner_response": valid_python,
        },
    )

    assert "syntax error" not in result["feedback"].lower()
    assert all(
        "syntax error" not in str(item).lower()
        for item in result["weaknesses"]
    )


def test_deterministic_quiz_criteria_override_ai_failure():
    service = AssessmentService(
        bedrock_evaluator=FakeBedrockEvaluator(),
    )

    valid_python = '''
questions = [
    {"question": "What keyword defines a function?", "answer": "def"},
    {"question": "What data type stores ordered items?", "answer": "list"},
]

def run_quiz():
    score = 0

    for item in questions:
        print(item["question"])
        answer = input("Your answer: ").strip().lower()

        if answer == item["answer"]:
            print("Correct!")
            score += 1

    print(f"Final score: {score}/{len(questions)}")

run_quiz()
'''

    result = service.evaluate(
        mission={"title": "Build a Command-Line Quiz"},
        attempt={
            "skill": "python",
            "attempt_type": "code",
            "learner_response": valid_python,
        },
    )

    assert result["score"] == 100
    assert result["passed"] is True
    assert result["passed_criteria"] == 5
    assert result["total_criteria"] == 5

def test_deterministic_expense_tracker_criteria_override_ai_failure():
    class FailingBedrockEvaluator:
        def evaluate(
            self,
            mission: dict[str, Any],
            attempt: dict[str, Any],
        ) -> dict[str, Any]:
            return {
                "score": 20,
                "passed": False,
                "criteria": [
                    {
                        "id": "expense_storage",
                        "name": "Store multiple expenses in a list",
                        "passed": False,
                        "evidence": "AI incorrectly reports that expenses are not stored.",
                    },
                    {
                        "id": "add_expense_function",
                        "name": "Use a function to add an expense",
                        "passed": False,
                        "evidence": "AI incorrectly reports that add_expense is missing.",
                    },
                    {
                        "id": "total_expense_function",
                        "name": "Use a function to calculate the total expenses",
                        "passed": False,
                        "evidence": "AI incorrectly reports that calculate_total is invalid.",
                    },
                    {
                        "id": "multiple_expenses",
                        "name": "Process multiple expenses using a loop",
                        "passed": False,
                        "evidence": "AI incorrectly reports that no loop is used.",
                    },
                    {
                        "id": "expense_summary",
                        "name": "Display the expenses and calculated total",
                        "passed": False,
                        "evidence": "AI incorrectly reports that the summary is missing.",
                    },
                ],
                "strengths": [],
                "weaknesses": ["AI-generated false negative."],
                "feedback": "AI-generated evaluation is intentionally incorrect.",
                "next_action": "Retry the mission.",
            }

    service = AssessmentService(
        bedrock_evaluator=FailingBedrockEvaluator(),
    )

    valid_python = '''
expenses = []


def add_expense(name, amount):
    expenses.append((name, amount))


def calculate_total():
    total = 0

    for name, amount in expenses:
        total += amount

    return total


def display_expenses():
    for name, amount in expenses:
        print(f"{name}: ${amount:.2f}")


add_expense("Food", 25.50)
add_expense("Transport", 15.00)
add_expense("Internet", 30.00)

display_expenses()
print(f"Total: ${calculate_total():.2f}")
'''

    result = service.evaluate(
        mission={
            "title": "Build a Function-Based Expense Tracker",
            "criteria": [
                {
                    "id": "expense_storage",
                    "name": "Store multiple expenses in a list",
                },
                {
                    "id": "add_expense_function",
                    "name": "Use a function to add an expense",
                },
                {
                    "id": "total_expense_function",
                    "name": "Use a function to calculate the total expenses",
                },
                {
                    "id": "multiple_expenses",
                    "name": "Process multiple expenses using a loop",
                },
                {
                    "id": "expense_summary",
                    "name": "Display the expenses and calculated total",
                },
            ],
        },
        attempt={
            "skill": "python",
            "attempt_type": "code",
            "learner_response": valid_python,
        },
    )

    assert result["score"] == 100
    assert result["passed"] is True
    assert result["passed_criteria"] == 5
    assert result["total_criteria"] == 5
