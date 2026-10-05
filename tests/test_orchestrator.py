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

def test_orchestrator_resolves_concept_for_canonical_mission():
    orchestrator = LearningOrchestrator(
        learner_id="concept-test",
        skill="Python",
        level="beginner",
    )

    orchestrator.record_mission({
        "id": "build-number-guessing-game",
        "title": "Build a Number Guessing Game",
    })

    concept = orchestrator.session.concept

    assert concept is not None
    assert concept["id"] == "python-variables"
    assert concept["title"] == "Variables"

def test_orchestrator_gets_capability_profile():

    class FakeMCPClient:
        async def call_tool(self, tool_name, arguments):
            assert tool_name == "get_capability_profile"
            assert arguments == {
                "learner_id": "capability-test-learner",
            }

            class Result:
                content = [
                    type(
                        "Content",
                        (),
                        {
                            "text": (
                                '{"status": "success", '
                                '"learner_id": "capability-test-learner", '
                                '"capabilities": ['
                                '{"skill": "Python", '
                                '"missions": 2, '
                                '"best_score": 100}'
                                ']}'
                            )
                        },
                    )()
                ]

            return Result()

    async def run():
        orchestrator = LearningOrchestrator(
            learner_id="capability-test-learner",
            skill="Python",
            level="beginner",
            mcp_client=FakeMCPClient(),
        )

        result = await orchestrator.get_capability_profile()

        assert result["status"] == "success"
        assert result["learner_id"] == "capability-test-learner"
        assert len(result["capabilities"]) == 1
        assert result["capabilities"][0]["skill"] == "Python"
        assert result["capabilities"][0]["missions"] == 2
        assert result["capabilities"][0]["best_score"] == 100

        state = orchestrator.get_state()

        assert state["capability_profile"] == result

    import asyncio

    asyncio.run(run())

def test_orchestrator_resolves_javascript_mission_by_id():
    orchestrator = LearningOrchestrator(
        learner_id="javascript-mission-test",
        skill="python",
        level="beginner",
        mission_id="build-console-to-do-list",
    )

    assert orchestrator.session.skill == "javascript"
    assert orchestrator.session.mission is not None
    assert (
        orchestrator.session.mission["id"]
        == "build-console-to-do-list"
    )
    assert (
        orchestrator.session.mission["title"]
        == "Build a Console To-Do List"
    )


def test_orchestrator_resolves_aws_mission_by_id():
    orchestrator = LearningOrchestrator(
        learner_id="aws-mission-test",
        skill="python",
        level="beginner",
        mission_id="build-serverless-hello-world-api",
    )

    assert orchestrator.session.skill == "aws-cloud"
    assert orchestrator.session.mission is not None
    assert (
        orchestrator.session.mission["id"]
        == "build-serverless-hello-world-api"
    )
    assert (
        orchestrator.session.mission["title"]
        == "Build a Serverless Hello World API"
    )


def test_orchestrator_resolves_python_mission_by_id():
    orchestrator = LearningOrchestrator(
        learner_id="python-mission-test",
        skill="python",
        level="beginner",
        mission_id="build-number-guessing-game",
    )

    assert orchestrator.session.skill == "python"
    assert orchestrator.session.mission is not None
    assert (
        orchestrator.session.mission["id"]
        == "build-number-guessing-game"
    )


def test_orchestrator_rejects_unknown_mission_id():
    try:
        LearningOrchestrator(
            learner_id="unknown-mission-test",
            skill="python",
            level="beginner",
            mission_id="does-not-exist",
        )
    except ValueError as exc:
        assert str(exc) == "Unknown mission ID: does-not-exist"
    else:
        raise AssertionError(
            "Expected ValueError for unknown mission ID."
        )

