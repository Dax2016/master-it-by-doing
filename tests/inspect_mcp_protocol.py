import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


SERVER_URL = "http://127.0.0.1:8000/mcp"


async def inspect():
    print("=" * 60)
    print("MASTER IT BY DOING — MCP PROTOCOL INSPECTION")
    print("=" * 60)

    async with streamablehttp_client(SERVER_URL) as (
        read_stream,
        write_stream,
        session_id,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            initialization = await session.initialize()

            print("\n--- Initialization ---")
            print(initialization)

            print("\n--- Server Capabilities ---")
            print(initialization.capabilities)

            print("\n--- Server Information ---")
            print(initialization.serverInfo)

            print("\n--- Protocol Version ---")
            print(initialization.protocolVersion)

            print("\n--- Session ID ---")
            print(session_id)

            tools = await session.list_tools()

            print("\n--- MCP Tools ---")

            for tool in tools.tools:
                print(f"\nName: {tool.name}")
                print(f"Description: {tool.description}")
                print(f"Input schema: {tool.inputSchema}")

    print("\n" + "=" * 60)
    print("MCP PROTOCOL INSPECTION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(inspect())