from services.assessment.ground_truth import GroundTruthEvaluator


def main() -> None:
    evaluator = GroundTruthEvaluator()

    mission = {
        "mission": "Build a Number Guessing Game",
    }

    bedrock_evaluation = {
        "score": 30,
        "passed": False,
        "criteria": [
            {
                "name": "Generate a random number between 1 and 10",
                "passed": True,
                "evidence": "random.randint(1, 10)",
            },
            {
                "name": "Prompt user for a guess",
                "passed": True,
                "evidence": "input()",
            },
            {
                "name": (
                    "Compare guess to the number "
                    "and provide appropriate feedback"
                ),
                "passed": False,
                "evidence": (
                    "Only equality is checked."
                ),
            },
            {
                "name": (
                    "Allow multiple guessing attempts "
                    "until correct"
                ),
                "passed": False,
                "evidence": (
                    "No loop is implemented."
                ),
            },
        ],
    }

    result = evaluator.evaluate(
        mission=mission,
        evaluation=bedrock_evaluation,
    )

    print("\n=== GROUND TRUTH RESULT ===")
    print(result)


if __name__ == "__main__":
    main()