import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from agent.mcp_client import MCPLearningClient


async def main():
    client = MCPLearningClient()

    async with streamablehttp_client(client.server_url) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            result = await session.list_tools()

            for tool in result.tools:
                print("=" * 70)
                print(f"TOOL: {tool.name}")
                print(f"DESCRIPTION: {tool.description}")
                print(f"SCHEMA: {tool.inputSchema}")


if __name__ == "__main__":
    asyncio.run(main())