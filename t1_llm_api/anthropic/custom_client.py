import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


class CustomAnthropicAIClient(AIClient):
    """
    Custom HTTP client for Anthropic's Claude API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with Claude's API directly
    and handle its Server-Sent Events (SSE) streaming format.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        body = {
            "model": self._model_name,
            "system": self._system_prompt,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": kwargs.get("max_tokens", 1024)
        }

        resp = requests.post(self._endpoint, headers=headers, json=body)

        if resp.status_code != 200:
            raise Exception(f"HTTP error {resp.status_code}: {resp.text}")

        text = resp.json()["content"][0]["text"]
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }

        body = {
            "model": self._model_name,
            "system": self._system_prompt,
            "messages": [m.to_dict() for m in messages],
            "max_tokens": kwargs.get("max_tokens", 1024),
            "stream": True
        }

        print("\nAI: ", end="", flush=True)
        full_text = ""

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(self._endpoint, headers=headers, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP error {resp.status}: {await resp.text()}")

                async for line in resp.content:
                    line = line.decode("utf-8").strip()

                    if not line.startswith("data: "):
                        continue

                    data = json.loads(line[len("data: "):])

                    if data.get("type") == "message_stop":
                        break

                    if data.get("type") == "content_block_delta":
                        delta = data.get("delta", {}).get("text", "")
                        if delta:
                            print(delta, end="", flush=True)
                            full_text += delta

        print()
        return Message(role=Role.ASSISTANT, content=full_text)

