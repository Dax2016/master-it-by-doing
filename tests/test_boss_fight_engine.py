import pytest

from services.assessment.boss_fight_engine import BossFightEngine
from services.learner.learner_state import LearnerState


@pytest.fixture
def setup_fight():
    engine = BossFightEngine()
    learner = LearnerState("learner-a")
    challenge = engine.create_challenge(
        learner,
        skill="Python",
        parent_mission_id="mission-python-1",
        parent_mission_title="Build a Number Guessing Game",
    )
    return engine, learner, challenge


def binding(challenge):
    return {
        "skill": challenge["skill"],
        "parent_mission_id": challenge["parent_mission_id"],
    }


def evaluation(learner, challenge, *, passed, passed_criteria, total_criteria):
    return {
        "status": "evaluated",
        "learner_id": learner.learner_id,
        "skill": challenge["skill"],
        "mission_id": challenge["parent_mission_id"],
        "passed": passed,
        "score": 100 if passed else 50,
        "passed_criteria": passed_criteria,
        "total_criteria": total_criteria,
    }


def test_new_challenge_has_unique_id_and_ready_status(setup_fight):
    engine, learner, challenge = setup_fight

    another = engine.create_challenge(
        learner, "Python", "mission-python-1"
    )

    assert challenge["id"] != another["id"]
    assert challenge["status"] == "ready"
    assert challenge["learner_id"] == learner.learner_id
    assert challenge["evaluation"] is None
    assert len(learner.to_dict()["boss_fights"]) == 2


def test_successful_evaluation_passes_challenge_without_completing_mission(
    setup_fight,
):
    engine, learner, challenge = setup_fight
    engine.start_challenge(learner, challenge["id"], **binding(challenge))

    result = engine.record_evaluation(
        learner,
        challenge["id"],
        **binding(challenge),
        evaluation=evaluation(
            learner, challenge, passed=True, passed_criteria=4, total_criteria=4
        ),
    )

    assert result["status"] == "passed"
    assert result["evaluation"]["passed"] is True
    assert learner.completed_missions == []
    assert learner.get_active_mission("Python") is None


def test_failed_evaluation_fails_challenge_without_completing_mission(
    setup_fight,
):
    engine, learner, challenge = setup_fight
    engine.start_challenge(learner, challenge["id"], **binding(challenge))

    result = engine.record_evaluation(
        learner,
        challenge["id"],
        **binding(challenge),
        evaluation=evaluation(
            learner, challenge, passed=False, passed_criteria=2, total_criteria=4
        ),
    )

    assert result["status"] == "failed"
    assert learner.completed_missions == []


def test_cannot_evaluate_before_starting(setup_fight):
    engine, learner, challenge = setup_fight

    with pytest.raises(ValueError, match="in-progress"):
        engine.record_evaluation(
            learner,
            challenge["id"],
            **binding(challenge),
            evaluation=evaluation(
                learner, challenge, passed=True, passed_criteria=4,
                total_criteria=4,
            ),
        )


def test_cannot_start_a_challenge_twice(setup_fight):
    engine, learner, challenge = setup_fight
    engine.start_challenge(learner, challenge["id"], **binding(challenge))

    with pytest.raises(ValueError, match="in state 'in_progress'"):
        engine.start_challenge(learner, challenge["id"], **binding(challenge))


def test_evaluation_must_match_learner_skill_and_parent_mission(setup_fight):
    engine, learner, challenge = setup_fight
    engine.start_challenge(learner, challenge["id"], **binding(challenge))

    bad_evaluations = [
        {
            **evaluation(
                learner, challenge, passed=True, passed_criteria=4,
                total_criteria=4,
            ),
            "learner_id": "someone-else",
        },
        {
            **evaluation(
                learner, challenge, passed=True, passed_criteria=4,
                total_criteria=4,
            ),
            "skill": "JavaScript",
        },
        {
            **evaluation(
                learner, challenge, passed=True, passed_criteria=4,
                total_criteria=4,
            ),
            "mission_id": "different-mission",
        },
    ]

    for bad in bad_evaluations:
        with pytest.raises(ValueError):
            engine.record_evaluation(
                learner, challenge["id"], **binding(challenge), evaluation=bad
            )

    assert challenge["status"] == "ready"
    assert learner.boss_fights[0]["status"] == "in_progress"


def test_learner_and_skill_are_isolated(setup_fight):
    engine, learner_a, challenge = setup_fight
    learner_b = LearnerState("learner-b")

    with pytest.raises(ValueError, match="not found"):
        engine.start_challenge(
            learner_b, challenge["id"], **binding(challenge)
        )

    with pytest.raises(ValueError, match="Skill does not match"):
        engine.start_challenge(
            learner_a,
            challenge["id"],
            skill="JavaScript",
            parent_mission_id=challenge["parent_mission_id"],
        )

    with pytest.raises(ValueError, match="Parent mission"):
        engine.start_challenge(
            learner_a,
            challenge["id"],
            skill="Python",
            parent_mission_id="different-mission",
        )


def test_inconsistent_pass_result_is_rejected(setup_fight):
    engine, learner, challenge = setup_fight
    engine.start_challenge(learner, challenge["id"], **binding(challenge))

    with pytest.raises(ValueError, match="conflicts"):
        engine.record_evaluation(
            learner,
            challenge["id"],
            **binding(challenge),
            evaluation=evaluation(
                learner, challenge, passed=True, passed_criteria=3,
                total_criteria=4,
            ),
        )

    assert learner.boss_fights[0]["status"] == "in_progress"
