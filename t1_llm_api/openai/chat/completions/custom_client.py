import json

import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIClient(BaseOpenAIClient):
    """
    Custom HTTP client for OpenAI Chat Completions API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, providing more control over the HTTP layer and demonstrating
    how to interact with the API directly.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        all_messages = [
            {"role": Role.SYSTEM.value, "content": self._system_prompt},
            *[message.to_dict() for message in messages],
        ]

        body = {
            "model": self._model_name,
            "messages": all_messages,
        }

        resp = requests.post(self._endpoint, headers=headers, json=body)

        if resp.status_code != 200:
            raise Exception(f"HTTP error {resp.status_code}: {resp.text}")

        text = resp.json()["choices"][0]["message"]["content"]
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        all_messages = [
            {"role": Role.SYSTEM.value, "content": self._system_prompt},
            *[message.to_dict() for message in messages],
        ]

        body = {
            "model": self._model_name,
            "messages": all_messages,
            "stream": True,
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

                    data = line[len("data: "):]

                    if data == "[DONE]":
                        break

                    chunk = json.loads(data)
                    delta = chunk["choices"][0]["delta"].get("content")
                    if delta:
                        print(delta, end="", flush=True)
                        full_text += delta

        print()
        return Message(role=Role.ASSISTANT, content=full_text)
