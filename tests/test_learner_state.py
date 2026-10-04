from services.learner.learner_state import LearnerState


def test_capability_evidence_is_aggregated_for_same_mission():
    learner = LearnerState(
        learner_id="test-learner",
    )

    first_capability = {
        "id": "capability-1",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-1",
        "mission": "Build a Number Guessing Game",
        "concept_id": "python-loops",
        "status": "demonstrated",
        "score": 80,
        "passed": True,
        "evidence_ids": ["evidence-1"],
        "demonstrated_criteria": [
            {"id": "random_number", "passed": True},
        ],
    }

    second_capability = {
        "id": "capability-2",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-1",
        "mission": "Build a Number Guessing Game",
        "concept_id": "python-loops",
        "status": "demonstrated",
        "score": 100,
        "passed": True,
        "evidence_ids": ["evidence-2"],
        "demonstrated_criteria": [
            {"id": "user_input", "passed": True},
        ],
    }

    learner.add_capability(first_capability)
    learner.add_capability(second_capability)

    assert len(learner.capabilities) == 1

    capability = learner.capabilities[0]

    assert capability["id"] == "capability-1"
    assert capability["evidence_ids"] == [
        "evidence-1",
        "evidence-2",
    ]
    assert capability["score"] == 100
    assert capability["best_score"] == 100
    assert capability["attempts"] == 2
    assert capability["demonstrated_criteria"] == [
        {"id": "random_number", "passed": True},
        {"id": "user_input", "passed": True},
    ]


def test_capabilities_remain_separate_for_different_missions():
    learner = LearnerState(
        learner_id="test-learner",
    )

    capability_one = {
        "id": "capability-1",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-1",
        "status": "demonstrated",
        "score": 100,
        "passed": True,
        "evidence_ids": ["evidence-1"],
        "demonstrated_criteria": [],
    }

    capability_two = {
        "id": "capability-2",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-2",
        "status": "demonstrated",
        "score": 100,
        "passed": True,
        "evidence_ids": ["evidence-2"],
        "demonstrated_criteria": [],
    }

    learner.add_capability(capability_one)
    learner.add_capability(capability_two)

    assert len(learner.capabilities) == 2

def test_capability_criteria_are_deduplicated_by_id():
    learner = LearnerState(
        learner_id="test-learner",
    )

    first_capability = {
        "id": "capability-1",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-1",
        "status": "demonstrated",
        "score": 80,
        "passed": True,
        "evidence_ids": ["evidence-1"],
        "demonstrated_criteria": [
            {
                "id": "expense_storage",
                "passed": True,
                "evidence": "Expenses stored in a list.",
            },
        ],
    }

    second_capability = {
        "id": "capability-2",
        "learner_id": "test-learner",
        "skill": "Python",
        "mission_id": "mission-1",
        "status": "demonstrated",
        "score": 100,
        "passed": True,
        "evidence_ids": ["evidence-2"],
        "demonstrated_criteria": [
            {
                "id": "expense_storage",
                "passed": True,
                "evidence": "Multiple expenses are stored in the list.",
            },
        ],
    }

    learner.add_capability(first_capability)
    learner.add_capability(second_capability)

    capability = learner.capabilities[0]

    assert len(capability["demonstrated_criteria"]) == 1
    assert capability["demonstrated_criteria"][0]["id"] == "expense_storage"
    assert capability["demonstrated_criteria"][0]["evidence"] == (
        "Multiple expenses are stored in the list."
    )
