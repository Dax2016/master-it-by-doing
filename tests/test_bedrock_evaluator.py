from services.assessment.bedrock_evaluator import BedrockEvaluator


def main() -> None:
    evaluator = BedrockEvaluator()

    mission = {
    "title": "Build a Number Guessing Game",
    "description": (
        "Create a Python program that generates a random number "
        "and lets the learner guess it."
    ),
    "criteria": [
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
}

    attempt = {
        "learner_id": "bedrock-test-learner",
        "submission": """
import random

number = random.randint(1, 10)
guess = int(input("Guess a number from 1 to 10: "))

if guess == number:
    print("Correct!")
else:
    print("Wrong guess.")
""",
    }

    result = evaluator.evaluate(
        mission=mission,
        attempt=attempt,
    )

    print("\n=== BEDROCK EVALUATION ===")
    print(result)


if __name__ == "__main__":
    main()