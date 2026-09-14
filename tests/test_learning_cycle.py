import asyncio

from agent.orchestrator import LearningOrchestrator


def test_complete_learning_cycle():
    async def run():
        orchestrator = LearningOrchestrator(
            learner_id="e2e-learner",
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
        # 2. Create practical mission
        # -----------------------------------------------------

        mission_result = await orchestrator.create_mission()

        assert mission_result is not None
        assert orchestrator.session.mission is not None

        # -----------------------------------------------------
        # 3. Submit learner work
        # -----------------------------------------------------

        learner_code = """
import random

number = random.randint(1, 10)

guess = int(input("Guess the number: "))

if guess == number:
    print("Correct!")
else:
    print("Try again!")
""".strip()

        attempt_result = await orchestrator.submit_attempt(
            attempt=learner_code,
            attempt_type="code",
        )

        assert attempt_result is not None
        assert orchestrator.session.attempt_text == learner_code

        # -----------------------------------------------------
        # 4. Evaluate attempt
        # -----------------------------------------------------

        evaluation_result = await orchestrator.evaluate_attempt()

        assert evaluation_result is not None
        assert orchestrator.session.evaluation is not None

        evaluation = orchestrator.session.evaluation

        # Verify semantic evaluation results.
        assert evaluation["status"] == "evaluated"
        assert evaluation["score"] == 75
        assert evaluation["passed"] is False
        assert evaluation["passed_criteria"] == 3
        assert evaluation["total_criteria"] == 4

        # The learner should fail specifically on the
        # multiple-attempts requirement.
        assert any(
            criterion["id"] == "multiple_attempts"
            and criterion["passed"] is False
            for criterion in evaluation["criteria"]
        )

        # -----------------------------------------------------
        # 5. Identify weaknesses
        # -----------------------------------------------------

        weakness_result = await orchestrator.identify_weaknesses()

        assert weakness_result is not None
        assert orchestrator.session.weaknesses is not None

        weaknesses = orchestrator.session.weaknesses

        assert weaknesses["status"] == "identified"
        assert len(weaknesses["weaknesses"]) > 0

        # -----------------------------------------------------
        # 6. Generate targeted exercise
        # -----------------------------------------------------

        exercise_result = (
            await orchestrator.generate_targeted_exercise()
        )

        assert exercise_result is not None
        assert (
            orchestrator.session.targeted_exercise
            is not None
        )

        targeted_exercise = (
            orchestrator.session.targeted_exercise
        )

        assert targeted_exercise["status"] == "created"

        # The generated exercise must directly target the
        # criterion the learner failed.
        assert "multiple_attempts" in (
            targeted_exercise["exercise"]["targeted_criteria"]
        )

        # -----------------------------------------------------
        # 7. Adapt learning mission
        # -----------------------------------------------------

        adapted_result = (
            await orchestrator.adapt_learning_mission()
        )

        assert adapted_result is not None
        assert (
            orchestrator.session.adapted_mission
            is not None
        )

        adapted_mission = (
            orchestrator.session.adapted_mission
        )

        assert adapted_mission["status"] == "adapted"

        # -----------------------------------------------------
        # 8. Verify final orchestration state
        # -----------------------------------------------------

        state = orchestrator.get_state()

        assert state["learner_id"] == "e2e-learner"
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

        # -----------------------------------------------------
        # Final diagnostic output
        # -----------------------------------------------------

        print("\n========================================")
        print("END-TO-END LEARNING CYCLE PASSED")
        print("========================================")
        print(f"Goal:              {state['goal']}")
        print(f"Mission:           {state['mission']}")
        print(f"Evaluation:        {state['evaluation']}")
        print(f"Weaknesses:        {state['weaknesses']}")
        print(
            f"Targeted Exercise: {state['targeted_exercise']}"
        )
        print(
            f"Adapted Mission:   {state['adapted_mission']}"
        )
        print(
            f"Next Action:       {state['next_action']}"
        )

    asyncio.run(run())

