import asyncio
import time

from agent.mcp_client import MCPLearningClient


def test_create_learning_goal_through_mcp():

    async def run():
        client = MCPLearningClient()

        start = time.perf_counter()

        result = await client.call_tool(
            "create_learning_goal",
            {
                "learner_id": "integration-test-learner",
                "skill": "Python",
                "level": "beginner",
            },
        )

        elapsed = time.perf_counter() - start

        print(f"\nMCP tool call: {elapsed:.2f}s")

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

    asyncio.run(run())