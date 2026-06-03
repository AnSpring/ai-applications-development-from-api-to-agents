from abc import abstractmethod, ABC
from typing import Optional, Any

from mcp import ClientSession
from mcp.types import CallToolResult, TextContent, GetPromptResult, ReadResourceResult, Resource, TextResourceContents, BlobResourceContents, Prompt
from pydantic import AnyUrl


class MCPClient(ABC):

    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None

    @abstractmethod
    async def __aenter__(self):
        ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def get_tools(self) -> list[dict[str, Any]]:
        if not self.session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        tools = await self.session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            }
            for tool in tools.tools
        ]

    async def call_tool(self, tool_name: str, tool_args: dict[str, Any]) -> Any:
        if not self.session:
            raise RuntimeError("MCP client not connected. Call connect() first.")

        tool_result: CallToolResult = await self.session.call_tool(tool_name, tool_args)
        content = tool_result.content[0]
        print(f"    ⚙️: {content}\n")
        if isinstance(content, TextContent):
            return content.text
        else:
            return content

    async def get_resources(self) -> list[Resource]:
        if not self.session:
            raise RuntimeError("MCP client not connected.")
        try:
            result = await self.session.list_resources()
            return result.resources
        except Exception as e:
            print(f"Error getting resources: {e}")
            return []

    async def get_resource(self, uri: AnyUrl) -> str:
        if not self.session:
            raise RuntimeError("MCP client not connected.")

        result = await self.session.read_resource(uri)
        content = result.contents[0]
        if isinstance(content, TextResourceContents):
            return content.text
        else:
            return content.blob

    async def get_prompts(self) -> list[Prompt]:
        if not self.session:
            raise RuntimeError("MCP client not connected.")
        try:
            result = await self.session.list_prompts()
            return result.prompts
        except Exception as e:
            print(f"Error getting prompts: {e}")
            return []

    async def get_prompt(self, name: str) -> str:
        if not self.session:
            raise RuntimeError("MCP client not connected.")

        prompt_result: GetPromptResult = await self.session.get_prompt(name)
        combined_content = ""
        for message in prompt_result.messages:
            if hasattr(message, 'content') and isinstance(message.content, TextContent):
                combined_content += message.content.text + "\n"
            elif hasattr(message, 'content') and isinstance(message.content, str):
                combined_content += message.content + "\n"
        return combined_content