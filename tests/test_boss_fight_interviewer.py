from unittest.mock import Mock

from services.assessment.boss_fight_interviewer import BossFightInterviewer


def test_generate_question_includes_latest_answer_and_prior_context():
    interviewer = BossFightInterviewer.__new__(BossFightInterviewer)
    interviewer.model_id = "test-model"
    interviewer.client = Mock()
    interviewer.client.converse.return_value = {
        "output": {
            "message": {
                "content": [
                    {
                        "text": (
                            "Your use of a loop handles repeated guesses. "
                            "How would you validate non-numeric input?"
                        )
                    }
                ]
            }
        }
    }

    mission = {
        "title": "Build a Number Guessing Game",
        "skill": "Python",
        "description": "Generate a number and accept repeated guesses.",
        "skills": ["loops", "input validation"],
        "criteria": [{"name": "Allow multiple attempts"}],
    }
    challenge = {
        "skill": "Python",
        "challenge_brief": {
            "instructions": "Explain your implementation and edge cases."
        },
    }
    transcript = [
        {
            "role": "examiner",
            "content": "How will your game handle repeated guesses?",
        },
        {
            "role": "learner",
            "content": "I use a while loop until the guess is correct.",
            "attempt_type": "text",
        },
    ]

    result = interviewer.generate_question(
        mission=mission,
        challenge=challenge,
        transcript=transcript,
    )

    assert "non-numeric input" in result
    interviewer.client.converse.assert_called_once()

    request = interviewer.client.converse.call_args.kwargs
    assert request["modelId"] == "test-model"

    prompt = request["messages"][0]["content"][0]["text"]
    assert "I use a while loop until the guess is correct." in prompt
    assert "How will your game handle repeated guesses?" in prompt
    assert "CONVERSATION SO FAR" in prompt


def test_generate_question_rejects_empty_model_response():
    interviewer = BossFightInterviewer.__new__(BossFightInterviewer)
    interviewer.model_id = "test-model"
    interviewer.client = Mock()
    interviewer.client.converse.return_value = {
        "output": {"message": {"content": [{"text": "   "}]}}
    }

    try:
        interviewer.generate_question(
            mission={"title": "Test", "skill": "Python"},
            challenge={"challenge_brief": {}},
            transcript=[],
        )
    except RuntimeError as exc:
        assert "empty follow-up question" in str(exc)
    else:
        raise AssertionError("Expected an empty-response RuntimeError")
