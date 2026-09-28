"""
Master It By Doing
MCP Client

Connects the Agent Orchestrator to the running
Master It By Doing MCP server.
"""

import os
from typing import Any, Dict

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPLearningClient:
    """Client for the Master It By Doing MCP server."""

    def __init__(
        self,
        server_url: str | None = None,
    ):
        self.server_url = (
            server_url
            or os.getenv(
                "MCP_SERVER_URL",
                "http://127.0.0.1:8000/mcp",
            )
        )

    async def list_tools(self) -> list[str]:
        """Return the tools exposed by the MCP server."""

        async with streamable_http_client(self.server_url) as (
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

                return [
                    tool.name
                    for tool in result.tools
                ]

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """Call an MCP learning tool."""

        async with streamable_http_client(self.server_url) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments=arguments,
                )

                return result
