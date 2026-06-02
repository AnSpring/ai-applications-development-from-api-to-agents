from openai import AsyncOpenAI, OpenAI

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.openai.base import BaseOpenAIClient


class OpenAIResponsesClient(BaseOpenAIClient):
    """
    Client for OpenAI Responses API using the official SDK.

    This implementation uses the official OpenAI Python library to interact
    with the Responses API, which uses 'instructions' instead of system messages
    and 'input' instead of messages.

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
        input_messages = [message.to_dict() for message in messages]

        result = self._client.responses.create(
            model=self._model_name,
            instructions=self._system_prompt,
            input=input_messages,
        )

        text = result.output_text
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        input_messages = [message.to_dict() for message in messages]

        print("\nAI: ", end="", flush=True)
        full_text = ""

        async with self._async_client.responses.stream(
            model=self._model_name,
            instructions=self._system_prompt,
            input=input_messages,
        ) as stream:
            async for event in stream:
                if event.type == "response.output_text.delta":
                    delta = event.delta
                    if delta:
                        print(delta, end="", flush=True)
                        full_text += delta

        print()
        return Message(role=Role.ASSISTANT, content=full_text)
