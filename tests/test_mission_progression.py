import asyncio
import uuid

from agent.orchestrator import LearningOrchestrator


def test_mission_progression_after_mastery():
    async def run():
        orchestrator = LearningOrchestrator(
            learner_id=f"progression-learner-{uuid.uuid4()}",
            skill="Python",
            level="beginner",
        )

        # -----------------------------------------------------
        # 1. Create learning goal
        # -----------------------------------------------------

        goal_result = await orchestrator.create_learning_goal()

        assert goal_result is not None
        assert orchestrator.session.goal is not None

        # -----------------------------------------------------
        # 2. Create first practical mission
        # -----------------------------------------------------

        mission_result = await orchestrator.create_mission()

        assert mission_result is not None
        assert orchestrator.session.mission is not None

        mission_1 = orchestrator.session.mission

        # Mission 1 should be the canonical Python beginner mission.
        assert mission_1["mission"]["title"] == "Build a Number Guessing Game"

        # -----------------------------------------------------
        # 3. Submit a complete solution
        # -----------------------------------------------------

        learner_code = """
import random

number = random.randint(1, 10)

while True:
    guess = int(input("Guess the number: "))

    if guess == number:
        print("Correct!")
        break
    elif guess < number:
        print("Too low!")
    else:
        print("Too high!")
""".strip()

        attempt_result = await orchestrator.submit_attempt(
            attempt=learner_code,
            attempt_type="code",
        )

        assert attempt_result is not None

        # -----------------------------------------------------
        # 4. Evaluate successful attempt
        # -----------------------------------------------------

        evaluation_result = await orchestrator.evaluate_attempt()

        assert evaluation_result is not None
        assert orchestrator.session.evaluation is not None

        evaluation = orchestrator.session.evaluation

        assert evaluation["score"] == 100
        assert evaluation["passed"] is True
        assert evaluation["mastery_status"] == "mastered"
        assert evaluation["passed_criteria"] == 4
        assert evaluation["total_criteria"] == 4

                # -----------------------------------------------------
        # 4b. Mastery evidence must persist in learner state
        # -----------------------------------------------------

        state_result = await orchestrator.get_learner_state()

        assert state_result is not None

        learner_state = state_result["learner"]

        assert "mastery" in learner_state
        assert "Python" in learner_state["mastery"]

        mission_mastery = learner_state["mastery"]["Python"][
            "Build a Number Guessing Game"
        ]

        assert mission_mastery["status"] == "mastered"
        assert mission_mastery["score"] == 100
        assert mission_mastery["passed"] is True
        assert mission_mastery["passed_criteria"] == 4
        assert mission_mastery["total_criteria"] == 4

        # -----------------------------------------------------
        # 4c. Evidence and capability must persist
        # -----------------------------------------------------

        assert "evidence" in learner_state
        assert "capabilities" in learner_state

        assert len(learner_state["evidence"]) == 1
        assert len(learner_state["capabilities"]) == 1

        evidence = learner_state["evidence"][0]
        capability = learner_state["capabilities"][0]

        assert evidence["learner_id"] == orchestrator.session.learner_id
        assert evidence["skill"] == "Python"
        assert evidence["mission_id"] == mission_1["mission"]["id"]
        assert evidence["score"] == 100
        assert evidence["passed"] is True
        assert evidence["passed_criteria"] == 4
        assert evidence["total_criteria"] == 4

        assert "evidence_id" in orchestrator.session.latest_attempt
        assert (
            orchestrator.session.latest_attempt["evidence_id"]
            == evidence["id"]
        )

        assert capability["learner_id"] == orchestrator.session.learner_id
        assert capability["skill"] == "Python"
        assert capability["mission_id"] == mission_1["mission"]["id"]
        assert capability["status"] == "demonstrated"
        assert capability["score"] == 100
        assert capability["passed"] is True
        assert capability["evidence_ids"] == [evidence["id"]]
        assert capability["demonstrated_criteria"]

        # -----------------------------------------------------
        # 5. Adapt after mastery
        # -----------------------------------------------------

        adapted_result = await orchestrator.adapt_learning_mission()

        assert adapted_result is not None
        assert orchestrator.session.adapted_mission is not None

        adapted_mission = orchestrator.session.adapted_mission

        assert adapted_mission["status"] == "adapted"

        # -----------------------------------------------------
        # 6. Mastery must trigger progression
        # -----------------------------------------------------

        assert (
            adapted_mission["next_action"]
            == "create_advanced_mission"
        )

        assert adapted_mission["next_mission"] is not None

        next_mission = adapted_mission["next_mission"]

        assert next_mission["title"] != mission_1["mission"]["title"]

        # The next mission must still be a Python mission.
        assert next_mission["skill"] == "Python"

        # -----------------------------------------------------
        # Final diagnostic output
        # -----------------------------------------------------

        print("\n========================================")
        print("MISSION PROGRESSION TEST")
        print("========================================")
        print(f"Mission 1:    {mission_1}")
        print(f"Evaluation:   {evaluation}")
        print(f"Next Mission: {next_mission}")

    asyncio.run(run())
