import pytest
from mcp_server import server


SKILL = "python"
MISSION_ID = "build-number-guessing-game"


@pytest.fixture
def learner_id():
    value = "boss-fight-mcp-test-learner"
    server.learners.pop(value, None)
    yield value
    server.learners.pop(value, None)


def mock_assessment(passed=True, passed_criteria=4, total_criteria=4):
    return {
        "score": 100 if passed else 75,
        "passed": passed,
        "passed_criteria": passed_criteria,
        "total_criteria": total_criteria,
        "status": "mastered" if passed else "needs_practice",
        "criteria": [
            {"id": f"criterion-{i}", "passed": i <= passed_criteria}
            for i in range(1, total_criteria + 1)
        ],
        "strengths": ["Clear control flow"],
        "weaknesses": [],
        "feedback": "Mock assessment feedback",
    }


def create_and_start(learner_id):
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


def test_create_rejects_unknown_parent_mission(learner_id):
    result = server.create_boss_fight(
        skill=SKILL,
        parent_mission_id="mission-that-does-not-exist",
        learner_id=learner_id,
    )

    assert result["status"] == "error"
    assert server.get_boss_fights(learner_id=learner_id)["boss_fights"] == []


def test_evaluation_before_start_is_rejected(learner_id, monkeypatch):
    created = server.create_boss_fight(
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    challenge_id = created["challenge"]["id"]

    def should_not_evaluate(**kwargs):
        pytest.fail("Assessment must not run before the challenge starts.")

    monkeypatch.setattr(
        server.assessment_service, "evaluate", should_not_evaluate
    )

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="I built the game.",
        learner_id=learner_id,
    )

    assert result["status"] == "error"


def test_passed_challenge_records_linked_evidence_without_advancing_mastery(
    learner_id, monkeypatch
):
    challenge_id = create_and_start(learner_id)

    monkeypatch.setattr(
        server.assessment_service,
        "evaluate",
        lambda **kwargs: mock_assessment(),
    )

    learner = server.learners[learner_id]
    protected_fields = (
        "mastery",
        "capabilities",
        "completed_missions",
        "active_mission",
        "active_missions",
        "active_practice",
        "active_practices",
        "strengths",
        "weaknesses",
    )
    before = {
        name: getattr(learner, name, None)
        for name in protected_fields
    }

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="My completed number guessing game",
        learner_id=learner_id,
    )

    assert result["status"] == "evaluated", result
    assert result["evaluation"]["passed"] is True
    assert result["evaluation"]["boss_fight_id"] == challenge_id

    challenge = server.get_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert challenge["challenge"]["status"] == "passed"

    assert len(learner.attempts) == 1
    assert len(learner.evidence) == 1

    evidence = learner.evidence[0]
    assert evidence["evidence_type"] == "boss_fight"
    assert evidence["boss_fight_id"] == challenge_id

    for name, previous_value in before.items():
        assert getattr(learner, name, None) == previous_value, name


def test_failed_challenge_records_failure_without_advancing_mastery(
    learner_id, monkeypatch
):
    challenge_id = create_and_start(learner_id)

    monkeypatch.setattr(
        server.assessment_service,
        "evaluate",
        lambda **kwargs: mock_assessment(
            passed=False, passed_criteria=3, total_criteria=4
        ),
    )

    learner = server.learners[learner_id]
    before_mastery = learner.mastery.copy()
    before_capabilities = learner.capabilities.copy()
    before_completed = list(learner.completed_missions)

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="My incomplete number guessing game",
        learner_id=learner_id,
    )

    assert result["status"] == "evaluated", result
    assert result["evaluation"]["passed"] is False
    assert len(learner.attempts) == 1
    assert len(learner.evidence) == 1
    assert learner.evidence[0]["passed"] is False

    challenge = server.get_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert challenge["challenge"]["status"] == "failed"

    assert learner.mastery == before_mastery
    assert learner.capabilities == before_capabilities
    assert learner.completed_missions == before_completed


def test_inconsistent_assessment_is_rejected_without_recording_evidence(
    learner_id, monkeypatch
):
    challenge_id = create_and_start(learner_id)

    monkeypatch.setattr(
        server.assessment_service,
        "evaluate",
        lambda **kwargs: mock_assessment(
            passed=True, passed_criteria=3, total_criteria=4
        ),
    )

    learner = server.learners[learner_id]

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="Test inconsistent evaluation",
        learner_id=learner_id,
    )

    assert result["status"] == "error"
    assert learner.attempts == []
    assert learner.evidence == []

    challenge = server.get_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert challenge["challenge"]["status"] == "in_progress"


def test_assessment_exception_does_not_record_attempt_or_evidence(
    learner_id, monkeypatch
):
    challenge_id = create_and_start(learner_id)

    def raise_assessment_error(**kwargs):
        raise RuntimeError("Simulated assessment failure")

    monkeypatch.setattr(
        server.assessment_service, "evaluate", raise_assessment_error
    )

    learner = server.learners[learner_id]

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="Test assessment error",
        learner_id=learner_id,
    )

    assert result["status"] == "error"
    assert learner.attempts == []
    assert learner.evidence == []

    challenge = server.get_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert challenge["challenge"]["status"] == "in_progress"


def test_get_challenge_list_and_skill_filter(learner_id):
    first_id = create_and_start(learner_id)

    second = server.create_boss_fight(
        skill=SKILL,
        parent_mission_id="build-command-line-quiz",
        learner_id=learner_id,
    )
    assert second["status"] == "created", second

    retrieved = server.get_boss_fight(
        challenge_id=first_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_id=learner_id,
    )
    assert retrieved["challenge"]["id"] == first_id

    all_challenges = server.get_boss_fights(learner_id=learner_id)
    assert len(all_challenges["boss_fights"]) == 2

    python_challenges = server.get_boss_fights(
        learner_id=learner_id, skill="Python"
    )
    assert len(python_challenges["boss_fights"]) == 2

    other_skill = server.get_boss_fights(
        learner_id=learner_id, skill="javascript"
    )
    assert other_skill["boss_fights"] == []


def test_invalid_attempt_type_is_rejected_without_assessment(
    learner_id, monkeypatch
):
    challenge_id = create_and_start(learner_id)

    def should_not_evaluate(**kwargs):
        pytest.fail("Assessment must not run for an invalid attempt type.")

    monkeypatch.setattr(
        server.assessment_service, "evaluate", should_not_evaluate
    )

    result = server.evaluate_boss_fight(
        challenge_id=challenge_id,
        skill=SKILL,
        parent_mission_id=MISSION_ID,
        learner_response="Some response",
        attempt_type="invalid-type",
        learner_id=learner_id,
    )

    assert result["status"] == "error"
    assert server.learners[learner_id].attempts == []
    assert server.learners[learner_id].evidence == []