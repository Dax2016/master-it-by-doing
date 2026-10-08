import asyncio
import uuid

from agent.orchestrator import LearningOrchestrator


def test_targeted_practice_lifecycle():
    async def run():
        learner_id = f"practice-lifecycle-{uuid.uuid4()}"

        # -----------------------------------------------------
        # 1. Start the learner journey
        # -----------------------------------------------------

        orchestrator = LearningOrchestrator(
            learner_id=learner_id,
            skill="Python",
            level="beginner",
        )

        await orchestrator.create_learning_goal()
        await orchestrator.create_mission()

        mission = orchestrator.session.mission

        assert mission is not None
        assert (
            mission["mission"]["title"]
            == "Build a Number Guessing Game"
        )

        # -----------------------------------------------------
        # 2. Submit an incomplete mission attempt
        # -----------------------------------------------------

        incomplete_code = """
import random

number = random.randint(1, 10)
guess = int(input("Guess the number: "))

if guess == number:
    print("Correct!")
else:
    print("Try again!")
""".strip()

        await orchestrator.submit_attempt(
            attempt=incomplete_code,
            attempt_type="code",
        )

        evaluation_result = await orchestrator.evaluate_attempt()

        assert evaluation_result is not None
        assert orchestrator.session.evaluation is not None

        evaluation = orchestrator.session.evaluation

        assert evaluation["passed"] is False
        assert any(
            criterion["id"] == "multiple_attempts"
            and criterion["passed"] is False
            for criterion in evaluation["criteria"]
        )

        # -----------------------------------------------------
        # 3. Identify the weakness
        # -----------------------------------------------------

        weaknesses = await orchestrator.identify_weaknesses()

        assert weaknesses is not None
        assert orchestrator.session.weaknesses is not None

        # -----------------------------------------------------
        # 4. Generate targeted practice
        # -----------------------------------------------------

        exercise_result = await orchestrator.generate_targeted_exercise()

        assert exercise_result is not None

        exercise = orchestrator.session.targeted_exercise

        assert exercise is not None
        assert (
            exercise["exercise"]["title"]
            == "Guessing Game Boss Fight: The Loop"
        )

        # -----------------------------------------------------
        # 5. Adapt the mission into active practice
        # -----------------------------------------------------

        adapted_result = await orchestrator.adapt_learning_mission()

        assert adapted_result is not None

        adapted = orchestrator.session.adapted_mission

        assert adapted is not None
        assert adapted["status"] == "adapted"
        assert adapted["mission_completed"] is False
        assert adapted["practice_completed"] is False

        # -----------------------------------------------------
        # 6. Practice must persist in learner state
        # -----------------------------------------------------

        state_result = await orchestrator.get_learner_state()

        learner_state = state_result["learner"]

        assert learner_state["active_practice"] is not None

        active_practice = learner_state["active_practice"]

        assert (
            active_practice["parent_mission_id"]
            == mission["mission"]["id"]
        )
        assert active_practice["status"] == "ready"
        assert "multiple_attempts" in active_practice["targeted_criteria"]

        # -----------------------------------------------------
        # 7. A fresh orchestrator must restore the practice
        # -----------------------------------------------------

        resumed = LearningOrchestrator(
            learner_id=learner_id,
            skill="Python",
            level="beginner",
        )

        await resumed.restore_active_practice()

        assert resumed.session.active_practice is not None
        assert (
            resumed.session.active_practice["parent_mission_id"]
            == mission["mission"]["id"]
        )

        # -----------------------------------------------------
        # 8. Submit the successful practice attempt
        # -----------------------------------------------------

        practice_code = """
import random

number = random.randint(1, 10)
attempts = 0

while True:
    guess = int(input("Guess the number: "))
    attempts += 1

    if guess == number:
        print("Correct!")
        print(f"Attempts: {attempts}")
        break
    elif guess < number:
        print("Too low!")
    else:
        print("Too high!")
""".strip()

        resumed.session.mission = mission

        await resumed.submit_attempt(
            attempt=practice_code,
            attempt_type="code",
        )

        practice_evaluation_result = await resumed.evaluate_attempt()

        assert practice_evaluation_result is not None
        assert resumed.session.evaluation is not None

        practice_evaluation = resumed.session.evaluation

        assert (
            "passed" in practice_evaluation
            and practice_evaluation["passed"] is True
        )

        # -----------------------------------------------------
        # 9. Practice success should adapt back to retry
        # -----------------------------------------------------

        practice_weaknesses = await resumed.identify_weaknesses()

        assert practice_weaknesses is not None

        practice_adaptation = await resumed.adapt_learning_mission()

        assert practice_adaptation["status"] == "adapted"
        assert practice_adaptation["practice_completed"] is True
        assert practice_adaptation["mission_completed"] is False
        assert (
            practice_adaptation["next_action"]
            == "retry_parent_mission"
        )

        # -----------------------------------------------------
        # 10. Practice must now be cleared
        # -----------------------------------------------------

        final_state = await resumed.get_learner_state()

        final_learner = final_state["learner"]

        assert final_learner["active_practice"] is None

        # Parent mission remains active for retry.
        assert final_learner["active_mission"] is not None
        assert (
            final_learner["active_mission"]["mission_id"]
            == mission["mission"]["id"]
        )

    asyncio.run(run())
