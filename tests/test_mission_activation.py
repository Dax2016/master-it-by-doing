import pytest

from mcp_server import server


@pytest.fixture
def learner_id():
    import uuid

    value = f"mission-activation-test-{uuid.uuid4()}"
    server.learners.pop(value, None)
    yield value
    server.learners.pop(value, None)


def test_activate_valid_mission_sets_skill_scoped_state(learner_id):
    result = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="Python",
        learner_id=learner_id,
    )

    assert result["status"] == "activated"
    assert result["skill"] == "python"
    assert result["mission"]["id"] == "build-number-guessing-game"

    learner = server.get_learner(learner_id)
    active = learner.get_active_mission("python")
    assert active["mission_id"] == "build-number-guessing-game"
    assert active["status"] == "in_progress"


def test_activate_same_mission_resumes_without_replacing_state(learner_id):
    first = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="python",
        learner_id=learner_id,
    )
    second = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="python",
        learner_id=learner_id,
    )

    assert first["status"] == "activated"
    assert second["status"] == "resumed"
    assert server.get_learner(learner_id).get_active_mission("python")[
        "mission_id"
    ] == "build-number-guessing-game"


def test_activate_unknown_mission_returns_not_found(learner_id):
    result = server.activate_mission(
        mission_id="mission-that-does-not-exist",
        skill="python",
        learner_id=learner_id,
    )

    assert result["status"] == "not_found"
    assert server.get_learner(learner_id).get_active_mission("python") is None


def test_activate_mission_with_wrong_skill_returns_mismatch(learner_id):
    result = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="AWS-Cloud",
        learner_id=learner_id,
    )

    assert result["status"] == "skill_mismatch"
    assert server.get_learner(learner_id).get_active_mission("aws-cloud") is None
    assert server.get_learner(learner_id).get_active_mission("python") is None


def test_activation_does_not_replace_different_in_progress_mission(learner_id):
    learner = server.get_learner(learner_id)
    learner.set_active_mission(
        {
            "id": "existing-python-mission",
            "title": "Existing Python Mission",
            "description": "Already in progress",
        },
        "Python",
    )

    result = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="python",
        learner_id=learner_id,
    )

    assert result["status"] == "conflict"
    assert result["active_mission"]["mission_id"] == "existing-python-mission"
    assert learner.get_active_mission("python")["mission_id"] == (
        "existing-python-mission"
    )


def test_python_activation_preserves_other_skill_missions(learner_id):
    learner = server.get_learner(learner_id)
    learner.set_active_mission(
        {
            "id": "existing-javascript-mission",
            "title": "Existing JavaScript Mission",
            "description": "JavaScript work",
        },
        "JavaScript",
    )
    learner.set_active_mission(
        {
            "id": "existing-aws-mission",
            "title": "Existing AWS Mission",
            "description": "AWS work",
        },
        "AWS-Cloud",
    )

    result = server.activate_mission(
        mission_id="build-number-guessing-game",
        skill="python",
        learner_id=learner_id,
    )

    assert result["status"] == "activated"
    assert learner.get_active_mission("python")["mission_id"] == (
        "build-number-guessing-game"
    )
    assert learner.get_active_mission("javascript")["mission_id"] == (
        "existing-javascript-mission"
    )
    assert learner.get_active_mission("aws_cloud")["mission_id"] == (
        "existing-aws-mission"
    )
