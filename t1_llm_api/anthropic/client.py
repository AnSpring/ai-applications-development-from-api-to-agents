from anthropic import Anthropic, AsyncAnthropic

from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


class AnthropicAIClient(AIClient):
    """
    Client for Anthropic's Claude API using the official SDK.

    This implementation uses the official Anthropic Python library to interact
    with Claude models, providing both synchronous and streaming response capabilities.

    Attributes:
        _client (Anthropic): Synchronous Anthropic client instance.
        _async_client (AsyncAnthropic): Asynchronous Anthropic client instance.
        Inherits all other attributes from AIClient.
    """

    def __init__(self, endpoint: str, model_name: str, api_key: str, system_prompt: str):
        super().__init__(
            endpoint=endpoint,
            model_name=model_name,
            api_key=api_key,
            system_prompt=system_prompt
        )
        self._client = Anthropic(api_key=api_key)
        self._async_client = AsyncAnthropic(api_key=api_key)

    def response(self, messages: list[Message], **kwargs) -> Message:
        result = self._client.messages.create(
            model=self._model_name,
            system=self._system_prompt,
            messages=[m.to_dict() for m in messages],
            max_tokens=kwargs.get("max_tokens", 1024)
        )

        text = result.content[0].text
        print(f"\nAI: {text}")
        return Message(role=Role.ASSISTANT, content=text)

    async def stream_response(self, messages: list[Message], **kwargs) -> Message:
        print("\nAI: ", end="", flush=True)
        full_text = ""

        async with self._async_client.messages.stream(
                model=self._model_name,
                system=self._system_prompt,
                messages=[m.to_dict() for m in messages],
                max_tokens=kwargs.get("max_tokens", 1024)
        ) as stream:
            async for text_delta in stream.text_stream:
                print(text_delta, end="", flush=True)
                full_text += text_delta

        print()
        return Message(role=Role.ASSISTANT, content=full_text)
