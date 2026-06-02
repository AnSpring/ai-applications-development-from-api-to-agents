from openai import AsyncOpenAI, OpenAI

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class OpenAIClient(BaseOpenAIClient):
    """
    Client for OpenAI Chat Completions API using the official SDK.

    This implementation uses the official OpenAI Python library to interact
    with the Chat Completions API, providing both synchronous and streaming
    response capabilities.

    Attributes:
        _client (OpenAI): Synchronous OpenAI client instance.
        _async_client (AsyncOpenAI): Asynchronous OpenAI client instance.
        Inherits all other attributes from BaseOpenAIClient.
    """

    def __init__(self, endpoint: str, model_name: str, system_prompt: str, api_key: str):
        super().__init__(
            endpoint=endpoint,
            model_name=model_name,
            system_prompt=system_prompt,
            api_key=api_key,
        )
        self._client = OpenAI(api_key=api_key)
        self._async_client = AsyncOpenAI(api_key=api_key)

    def response(self, messages: list[Message], **kwargs) -> Message:
        all_messages = [
            {"role": Role.SYSTEM.value, "content": self._system_prompt},
            *[message.to_dict() for message in messages],
        ]

        result = self._client.chat.completions.create(
            model=self._model_name,
            messages=all_messages,
        )

        text = result.choices[0].message.content
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        all_messages = [
            {"role": Role.SYSTEM.value, "content": self._system_prompt},
            *[message.to_dict() for message in messages],
        ]

        stream = await self._async_client.chat.completions.create(
            model=self._model_name,
            messages=all_messages,
            stream=True,
        )

        print("\nAI: ", end="", flush=True)
        full_text = ""
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                full_text += delta
        print()

        return Message(role=Role.ASSISTANT, content=full_text)
