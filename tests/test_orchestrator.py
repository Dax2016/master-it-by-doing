from agent.orchestrator import LearningOrchestrator


def test_orchestrator_learning_flow():
    orchestrator = LearningOrchestrator(
        learner_id="demo-learner",
        skill="Python",
        level="beginner",
    )

    # ---------------------------------------------------------
    # Initial state
    # ---------------------------------------------------------

    assert orchestrator.next_action() == "create_learning_goal"

    # ---------------------------------------------------------
    # Goal
    # ---------------------------------------------------------

    orchestrator.record_goal({
        "status": "created",
        "skill": "Python",
    })

    assert orchestrator.next_action() == "create_mission"

    # ---------------------------------------------------------
    # Mission
    # ---------------------------------------------------------

    orchestrator.record_mission({
        "title": "Number Guessing Game",
    })

    assert orchestrator.next_action() == "submit_attempt"

    # ---------------------------------------------------------
    # Learner attempt
    # ---------------------------------------------------------

    orchestrator.record_attempt({
        "code": "print('hello')",
        "attempt_type": "code",
    })

    assert orchestrator.next_action() == "evaluate_attempt"

    # ---------------------------------------------------------
    # Evaluation
    # ---------------------------------------------------------

    orchestrator.record_evaluation({
        "score": 75,
        "passed": False,
        "failed_criteria": [
            {
                "criterion": "multiple_attempts",
                "passed": False,
            }
        ],
    })

    assert orchestrator.next_action() == "identify_weaknesses"

    # ---------------------------------------------------------
    # Weakness identification
    # ---------------------------------------------------------

    orchestrator.record_weaknesses({
        "weaknesses": [
            "multiple_attempts",
        ],
    })

    assert (
        orchestrator.next_action()
        == "generate_targeted_exercise"
    )

    # ---------------------------------------------------------
    # Targeted exercise
    # ---------------------------------------------------------

    orchestrator.record_targeted_exercise({
        "title": "Loop Practice",
        "description": (
            "Modify the guessing game so the learner "
            "can make multiple attempts."
        ),
    })

    assert (
        orchestrator.next_action()
        == "adapt_learning_mission"
    )

    # ---------------------------------------------------------
    # Adapted mission
    # ---------------------------------------------------------

    orchestrator.record_adapted_mission({
        "title": "Guessing Game Boss Fight",
        "mission": (
            "Build a guessing game using a loop that "
            "continues until the correct number is guessed."
        ),
    })

    # ---------------------------------------------------------
    # Cycle complete
    # ---------------------------------------------------------

    assert orchestrator.next_action() == "continue_learning"


def test_orchestrator_state_contains_learning_progress():
    orchestrator = LearningOrchestrator(
        learner_id="state-test-learner",
        skill="Python",
        level="beginner",
    )

    orchestrator.record_goal({
        "status": "created",
        "skill": "Python",
    })

    orchestrator.record_mission({
        "title": "Build a Calculator",
    })

    orchestrator.record_attempt({
        "code": "print(1 + 1)",
        "attempt_type": "code",
    })

    orchestrator.record_evaluation({
        "score": 80,
        "passed": True,
    })

    orchestrator.record_weaknesses({
        "weaknesses": [],
    })

    orchestrator.record_targeted_exercise({
        "title": "Calculator Extension",
    })

    orchestrator.record_adapted_mission({
        "title": "Calculator Challenge",
    })

    state = orchestrator.get_state()

    assert state["learner_id"] == "state-test-learner"
    assert state["skill"] == "Python"
    assert state["level"] == "beginner"

    assert state["goal"] is not None
    assert state["mission"] is not None
    assert state["latest_attempt"] is not None
    assert state["evaluation"] is not None
    assert state["weaknesses"] is not None
    assert state["targeted_exercise"] is not None
    assert state["adapted_mission"] is not None

    assert state["next_action"] == "continue_learning"


def test_orchestrator_records_original_attempt():
    orchestrator = LearningOrchestrator(
        learner_id="attempt-test",
        skill="Python",
        level="beginner",
    )

    code = """
name = input("What is your name? ")
print(f"Hello {name}")
""".strip()

    orchestrator.record_attempt({
        "learner_response": code,
        "attempt_type": "code",
    })

    assert orchestrator.session.attempt_text == code
    assert orchestrator.session.attempt_type == "code"


def test_orchestrator_next_action_sequence():
    orchestrator = LearningOrchestrator(
        learner_id="sequence-test",
        skill="Python",
        level="beginner",
    )

    expected_sequence = [
        "create_learning_goal",
        "create_mission",
        "submit_attempt",
        "evaluate_attempt",
        "identify_weaknesses",
        "generate_targeted_exercise",
        "adapt_learning_mission",
    ]

    assert orchestrator.next_action() == expected_sequence[0]

    orchestrator.record_goal({
        "skill": "Python",
    })

    assert orchestrator.next_action() == expected_sequence[1]

    orchestrator.record_mission({
        "title": "Python Mission",
    })

    assert orchestrator.next_action() == expected_sequence[2]

    orchestrator.record_attempt({
        "learner_response": "print('hello')",
        "attempt_type": "code",
    })

    assert orchestrator.next_action() == expected_sequence[3]

    orchestrator.record_evaluation({
        "score": 50,
        "passed": False,
    })

    assert orchestrator.next_action() == expected_sequence[4]

    orchestrator.record_weaknesses({
        "weaknesses": ["loops"],
    })

    assert orchestrator.next_action() == expected_sequence[5]

    orchestrator.record_targeted_exercise({
        "title": "Loop Practice",
    })

    assert orchestrator.next_action() == expected_sequence[6]

    orchestrator.record_adapted_mission({
        "title": "Loop Boss Fight",
    })

    assert orchestrator.next_action() == "continue_learning"