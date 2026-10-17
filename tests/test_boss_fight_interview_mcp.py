import pytest
from mcp_server import server


SKILL = "python"
MISSION_ID = "build-number-guessing-game"


@pytest.fixture
def learner_id():
    value = "boss-fight-interview-regression-learner"
    server.learners.pop(value, None)
    yield value
    server.learners.pop(value, None)


def start_challenge(learner_id):
    created = server.create_boss_fight(
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert created["status"] == "created", created

    challenge_id = created["challenge"]["id"]
    started = server.start_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert started["status"] == "started", started
    return challenge_id


def continue_interview(challenge_id, learner_id, response=""):
    return server.continue_boss_fight_interview(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response=response,
        attempt_type="text",
        learner_id=learner_id,
    )


def test_interview_preserves_answers_and_context_across_turns(
    learner_id, monkeypatch
):
    challenge_id = start_challenge(learner_id)
    received_transcripts = []

    questions = iter([
        "How does your game handle repeated guesses?",
        "How would you validate non-numeric input?",
        "What tests would prove your validation works?",
    ])

    def fake_generate_question(*, mission, challenge, transcript):
        received_transcripts.append([dict(turn) for turn in transcript])
        return next(questions)

    monkeypatch.setattr(
        server.boss_fight_interviewer,
        "generate_question",
        fake_generate_question,
    )

    # Opening turn: no learner answer should be fabricated.
    opening = continue_interview(challenge_id, learner_id)
    assert opening["status"] == "interview_continued", opening
    assert received_transcripts[0] == []
    assert opening["challenge"]["interview_transcript"][-1]["content"] == (
        "How does your game handle repeated guesses?"
    )

    first_answer = "I use a while loop until the guess is correct."
    second_answer = "I convert the input and catch ValueError."

    # The next prompt must contain both the previous question and this answer.
    second = continue_interview(challenge_id, learner_id, first_answer)
    assert second["status"] == "interview_continued", second

    second_prompt = received_transcripts[1]
    assert [turn["role"] for turn in second_prompt] == ["examiner", "learner"]
    assert second_prompt[-1]["content"] == first_answer
    assert second_prompt[0]["content"] == (
        "How does your game handle repeated guesses?"
    )

    # The following prompt must retain the entire earlier exchange too.
    third = continue_interview(challenge_id, learner_id, second_answer)
    assert third["status"] == "interview_continued", third

    third_prompt = received_transcripts[2]
    assert [turn["role"] for turn in third_prompt] == [
        "examiner", "learner", "examiner", "learner"
    ]
    assert third_prompt[1]["content"] == first_answer
    assert third_prompt[2]["content"] == (
        "How would you validate non-numeric input?"
    )
    assert third_prompt[3]["content"] == second_answer

    # Persisted transcript must alternate correctly across all three turns.
    transcript = third["challenge"]["interview_transcript"]
    assert [turn["role"] for turn in transcript] == [
        "examiner", "learner", "examiner", "learner", "examiner"
    ]
    assert transcript[1]["content"] == first_answer
    assert transcript[3]["content"] == second_answer
    assert transcript[-1]["content"] == (
        "What tests would prove your validation works?"
    )


def test_empty_follow_up_does_not_call_interviewer_or_change_transcript(
    learner_id, monkeypatch
):
    challenge_id = start_challenge(learner_id)
    monkeypatch.setattr(
        server.boss_fight_interviewer,
        "generate_question",
        lambda **kwargs: "What does your loop do?",
    )

    opening = continue_interview(challenge_id, learner_id)
    assert opening["status"] == "interview_continued", opening
    before = opening["challenge"]["interview_transcript"]

    def should_not_generate(**kwargs):
        pytest.fail("Interviewer must not run without a learner answer.")

    monkeypatch.setattr(
        server.boss_fight_interviewer,
        "generate_question",
        should_not_generate,
    )

    result = continue_interview(challenge_id, learner_id, "   ")
    assert result["status"] == "error"

    current = server.get_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert current["challenge"]["interview_transcript"] == before
