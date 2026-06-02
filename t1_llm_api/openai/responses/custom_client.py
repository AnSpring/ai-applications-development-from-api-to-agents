import json
import aiohttp
import requests

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class CustomOpenAIResponsesClient(BaseOpenAIClient):
    """
    Custom HTTP client for OpenAI Responses API.

    This implementation uses raw HTTP requests (requests/aiohttp) instead of
    the official SDK, demonstrating how to interact with the Responses API directly
    and handle its unique event-based streaming format.
    """

    def response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }

        body = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": [m.to_dict() for m in messages]
        }

        resp = requests.post(self._endpoint, headers=headers, json=body)

        if resp.status_code != 200:
            raise Exception(f"HTTP error {resp.status_code}: {resp.text}")

        text = resp.json()["output_text"]
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json"
        }

        body = {
            "model": self._model_name,
            "instructions": self._system_prompt,
            "input": [m.to_dict() for m in messages],
            "stream": True
        }

        print("\nAI: ", end="", flush=True)
        full_text = ""
        current_event = None

        connector = aiohttp.TCPConnector(ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(self._endpoint, headers=headers, json=body) as resp:
                if resp.status != 200:
                    raise Exception(f"HTTP error {resp.status}: {await resp.text()}")

                async for line in resp.content:
                    line = line.decode("utf-8").strip()

                    if line.startswith("event: "):
                        current_event = line[len("event: "):]

                    elif line.startswith("data: "):
                        if current_event != "response.output_text.delta":
                            continue

                        data = json.loads(line[len("data: "):])
                        delta = data.get("delta", "")
                        if delta:
                            print(delta, end="", flush=True)
                            full_text += delta

        print()
        return Message(role=Role.ASSISTANT, content=full_text)
