import asyncio
from typing import Any

from agent.mcp_client import MCPLearningClient


class AlexaLearningAssistant:
    """
    Alexa-facing learning assistant for Master It By Doing.

    Alexa handles the conversational experience.
    The MCP server handles the learning logic.
    """

    def __init__(self, learner_id: str = "demo-learner") -> None:
        self.client = MCPLearningClient()
        self.learner_id = learner_id.strip()
        if not self.learner_id:
            raise ValueError("learner_id must not be empty.")

    async def start_learning(
        self,
        skill: str,
        learner_level: str = "beginner",
    ) -> dict[str, Any]:
        """Start a practical learning journey."""

        goal_result = await self.client.call_tool(
            "create_learning_goal",
            {
                "skill": skill.strip().lower(),
                "learner_level": learner_level,
                "learner_id": self.learner_id,
            },
        )

        mission_result = await self.client.call_tool(
            "create_mission",
            {
                "skill": skill.strip().lower(),
                "learner_level": learner_level,
                "learner_id": self.learner_id,
            },
        )

        return {
            "goal": goal_result,
            "mission": mission_result,
        }


async def demo() -> None:
    print("=" * 60)
    print("MASTER IT BY DOING")
    print("Alexa+ Learning Assistant")
    print("=" * 60)

    assistant = AlexaLearningAssistant()

    print("\nLearner:")
    print("Alexa, help me learn Python.")

    print("\nAlexa+:")
    print("Absolutely. What would you like to build?")

    print("\nLearner:")
    print("A number guessing game.")

    print("\nAlexa+:")
    print(
        "Great choice. We'll learn Python by building "
        "a number guessing game."
    )

    result = await assistant.start_learning(
        skill="Python",
        learner_level="beginner",
    )

    print("\n--- GOAL RESULT ---")
    print(result["goal"])

    print("\n--- MISSION RESULT ---")
    print(result["mission"])

    print("\nAlexa+:")
    print(
        "Your learning mission is ready. "
        "Let's start building."
    )

    print("\n" + "=" * 60)
    print("ALEXA LEARNING JOURNEY STARTED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo())