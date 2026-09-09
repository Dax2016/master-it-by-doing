import asyncio

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
            # ---------------------------------------------------------
            # 7. IDENTIFY WEAKNESSES
            # ---------------------------------------------------------
            weakness_analysis = await session.call_tool(
                "identify_weaknesses",
                {
                    "skill": "Python",
                    "evaluation": {
                        "status": "evaluated",
                        "strengths": [
                            "Result feedback"
                        ],
                        "weaknesses": [
                            "Random number generation",
                            "Learner input",
                            "Guess comparison",
                            "Conditional logic",
                            "Python implementation",
                        ],
                    },
                },
            )

            print("\nWEAKNESS ANALYSIS:")
            print(weakness_analysis)            


if __name__ == "__main__":
    asyncio.run(main())