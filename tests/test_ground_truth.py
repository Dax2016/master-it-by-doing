from services.assessment.ground_truth import GroundTruthEvaluator


def test_command_line_quiz_ground_truth_does_not_trust_ai_pass_fail():
    evaluator = GroundTruthEvaluator()

    mission = {
        "mission": "Build a Command-Line Quiz",
    }

    bedrock_evaluation = {
        "score": 80,
        "passed": False,
        "criteria": [
            {
                "id": "quiz_questions",
                "name": "Ask multiple quiz questions",
                "passed": True,
                "evidence": "Questions are iterated.",
            },
            {
                "id": "answer_checking",
                "name": "Check whether each answer is correct",
                "passed": True,
                "evidence": "Answers are compared.",
            },
            {
                "id": "score_tracking",
                "name": "Track the learner's score",
                "passed": True,
                "evidence": "Score increments.",
            },
            {
                "id": "multiple_questions",
                "name": "Process multiple questions in a loop",
                "passed": True,
                "evidence": "A for loop processes questions.",
            },
            {
                "id": "final_score",
                "name": "Display the final quiz score",
                "passed": False,
                "evidence": "AI failed to identify the final score.",
            },
        ],
        "validation": {
            "python_syntax": {
                "syntax_valid": True,
                "error": None,
                "criteria": {
                    "quiz_questions": True,
                    "answer_checking": True,
                    "score_tracking": True,
                    "multiple_questions": True,
                    "final_score": True,
                },
            },
        },
    }

    result = evaluator.evaluate(
        mission=mission,
        evaluation=bedrock_evaluation,
    )

    assert result["score"] == 100
    assert result["passed"] is True
    assert result["passed_criteria"] == 5
    assert result["total_criteria"] == 5
    assert result["status"] == "mastered"