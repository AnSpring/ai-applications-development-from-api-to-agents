import os
import sys
import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from mcp import Resource
from mcp.types import Prompt

from commons.constants import OPENAI_API_KEY
from commons.models.message import Message
from commons.models.role import Role
from t9_mcp_fundamentals.agent.agent import AgentMCPFundamentals
from t9_mcp_fundamentals.agent.mcp_clients.http import HttpMCPClient
from t9_mcp_fundamentals.agent.mcp_clients.stdio import StdioMCPClient
from t9_mcp_fundamentals.agent.prompts import SYSTEM_PROMPT




async def main():
    async with HttpMCPClient(mcp_server_url="http://localhost:8005/mcp") as mcp_client:

        # 2. Print Available Resources
        resources: list[Resource] = await mcp_client.get_resources()
        print(f"\n📦 Available Resources: {[str(r.uri) for r in resources]}")

        # 3. Print Available Tools
        tools = await mcp_client.get_tools()
        print(f"\n🔧 Available Tools: {[t['function']['name'] for t in tools]}")

        # 4. Create Agent
        agent = AgentMCPFundamentals(
            api_key=OPENAI_API_KEY,
            model="gpt-4o",
            tools=tools,
            mcp_client=mcp_client
        )

        # 5. System prompt
        messages = [Message(role=Role.SYSTEM, content=SYSTEM_PROMPT)]

        # 6. Print Available Prompts
        prompts: list[Prompt] = await mcp_client.get_prompts()
        print(f"\n📝 Available Prompts: {[p.name for p in prompts]}")

        # 7. Infinite loop
        while True:
            user_input = input("\n> ").strip()

            if user_input.lower() == "exit":
                break

            messages.append(Message(role=Role.USER, content=user_input))
            ai_message = await agent.get_response(messages)
            messages.append(ai_message)


if __name__ == "__main__":
    asyncio.run(main())
