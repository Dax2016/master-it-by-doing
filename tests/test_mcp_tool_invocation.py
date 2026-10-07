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
def test_get_concepts_through_mcp():

    async def run():
        client = MCPLearningClient()

        result = await client.call_tool(
            "get_concepts",
            {
                "skill": "Python",
            },
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        text = result.content[0].text

        assert "python-loops" in text
        assert "Loops" in text
        assert "examples" in text
        assert "practice" in text

    asyncio.run(run())

def test_get_capability_profile_through_mcp():

    async def run():
        client = MCPLearningClient()

        result = await client.call_tool(
            "get_capability_profile",
            {
                "learner_id": "integration-test-learner",
            },
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        text = result.content[0].text

        assert '"status": "success"' in text
        assert '"learner_id": "integration-test-learner"' in text
        assert '"capabilities":' in text

    asyncio.run(run())

def test_get_learner_profile_through_mcp():
    async def run():
        client = MCPLearningClient()

        result = await client.call_tool(
            "get_learner_profile",
            {
                "learner_id": "profile-mcp-test-learner",
            },
        )

        assert result is not None
        assert hasattr(result, "content")
        assert len(result.content) > 0

        text = result.content[0].text

        assert "profile-mcp-test-learner" in text

    asyncio.run(run())