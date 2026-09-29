import asyncio

from agent.mcp_client import MCPLearningClient


def test_mcp_client_lists_learning_tools():
    async def run():
        client = MCPLearningClient()

        tools = await client.list_tools()

        expected_tools = {
            "create_learning_goal",
            "create_mission",
            "get_concepts",
            "submit_attempt",
            "evaluate_attempt",
            "identify_weaknesses",
            "generate_targeted_exercise",
            "adapt_learning_mission",
            "get_learner_state",
        }

        assert expected_tools.issubset(set(tools))

    asyncio.run(run())
