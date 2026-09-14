import asyncio
import json

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read, write, _):

        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()

            print("TOOLS:")
            for tool in tools.tools:
                print(f"- {tool.name}")

            # ---------------------------------------------------------
            # 1. CREATE LEARNING GOAL
            # ---------------------------------------------------------
            goal = await session.call_tool(
                "create_learning_goal",
                {
                    "skill": "Python",
                    "learner_level": "beginner",
                },
            )

            print("\nLEARNING GOAL:")
            print(goal)

            # ---------------------------------------------------------
            # 2. CREATE MISSION
            # ---------------------------------------------------------
            mission = await session.call_tool(
                "create_mission",
                {
                    "skill": "Python",
                    "learner_level": "beginner",
                },
            )

            print("\nMISSION:")
            print(mission)

            # ---------------------------------------------------------
            # 3. SUBMIT GOOD ATTEMPT
            # ---------------------------------------------------------
            good_solution = (
                "import random\n\n"
                "number = random.randint(1, 10)\n"
                "guess = int(input('Guess the number: '))\n\n"
                "if guess == number:\n"
                "    print('Correct!')\n"
                "else:\n"
                "    print('Try again!')"
            )

            attempt = await session.call_tool(
                "submit_attempt",
                {
                    "skill": "Python",
                    "mission": "Build a Number Guessing Game",
                    "learner_response": good_solution,
                    "attempt_type": "code",
                },
            )

            print("\nGOOD ATTEMPT:")
            print(attempt)

            # ---------------------------------------------------------
            # 4. EVALUATE GOOD ATTEMPT
            # ---------------------------------------------------------
            evaluation = await session.call_tool(
                "evaluate_attempt",
                {
                    "skill": "Python",
                    "mission": "Build a Number Guessing Game",
                    "learner_response": good_solution,
                    "attempt_type": "code",
                },
            )

            print("\nGOOD ATTEMPT EVALUATION:")
            print(evaluation)

            evaluation_data = json.loads(
                evaluation.content[0].text
            )
            assert evaluation_data["status"] == "evaluated"
            assert evaluation_data["score"] == 75
            assert evaluation_data["passed_criteria"] == 3
            assert evaluation_data["total_criteria"] == 4
            assert evaluation_data["mastery_status"] == "needs_practice"

            # ---------------------------------------------------------
            # 5. SUBMIT WEAK ATTEMPT
            # ---------------------------------------------------------
            weak_solution = "print('Hello world')"

            weak_attempt = await session.call_tool(
                "submit_attempt",
                {
                    "skill": "Python",
                    "mission": "Build a Number Guessing Game",
                    "learner_response": weak_solution,
                    "attempt_type": "code",
                },
            )

            print("\nWEAK ATTEMPT:")
            print(weak_attempt)

            # ---------------------------------------------------------
            # 6. EVALUATE WEAK ATTEMPT
            # ---------------------------------------------------------
            weak_evaluation = await session.call_tool(
                "evaluate_attempt",
                {
                    "skill": "Python",
                    "mission": "Build a Number Guessing Game",
                    "learner_response": weak_solution,
                    "attempt_type": "code",
                },
            )

            print("\nWEAK ATTEMPT EVALUATION:")
            print(weak_evaluation)

            weak_evaluation_data = json.loads(
                weak_evaluation.content[0].text
            )
            assert weak_evaluation_data["status"] == "evaluated"
            assert weak_evaluation_data["score"] == 0
            assert weak_evaluation_data["passed_criteria"] == 0
            assert weak_evaluation_data["total_criteria"] == 4

            # ---------------------------------------------------------
            # 7. IDENTIFY WEAKNESSES
            # ---------------------------------------------------------
            weakness_analysis = await session.call_tool(
                "identify_weaknesses",
                {
                    "skill": "Python",
                    "evaluation": weak_evaluation_data,
                },
            )

            print("\nWEAKNESS ANALYSIS:")
            print(weakness_analysis)

            # ---------------------------------------------------------
            # 8. GENERATE TARGETED EXERCISE
            # ---------------------------------------------------------
            weakness_data = json.loads(
                weakness_analysis.content[0].text
            )

            targeted_exercise = await session.call_tool(
            "generate_targeted_exercise",
            {
                "skill": "Python",
                "failed_criteria": [
            criterion
            for criterion in evaluation_data["criteria"]
            if not criterion["passed"]
               ],
               },
            )
            # ---------------------------------------------------------
            # 9. ADAPT LEARNING MISSION
            # ---------------------------------------------------------
            adapted_mission = await session.call_tool(
                "adapt_learning_mission",
                {
                    "skill": "Python",
                    "evaluation": evaluation_data,
                },
            )
            adapted_mission_data = json.loads(
                adapted_mission.content[0].text
            )
            targeted_exercise_data = adapted_mission_data[
                "targeted_exercise"
            ]["exercise"]
            assert (
                targeted_exercise_data["title"]
                == "Guessing Game Boss Fight: The Loop"
            )
            assert targeted_exercise_data["targeted_criteria"] == [
                "multiple_attempts"
            ]
                        # ---------------------------------------------------------
            # 10. GET LEARNER STATE
            # ---------------------------------------------------------
            learner_state = await session.call_tool(
                "get_learner_state",
                {},
            )

            print("\nLEARNER STATE:")
            print(learner_state)

            print("\nADAPTED LEARNING MISSION:")
            print(adapted_mission)

            print("\nTARGETED EXERCISE:")
            print(targeted_exercise)


if __name__ == "__main__":
    asyncio.run(main())