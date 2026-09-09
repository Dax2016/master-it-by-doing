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

            result = await session.call_tool(
                "create_learning_goal",
                {
                    "skill": "Python",
                    "learner_level": "beginner",
                },
            )

            print("\nRESULT:")
            print(result)


if __name__ == "__main__":
    asyncio.run(main())