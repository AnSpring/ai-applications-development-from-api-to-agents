from abc import ABC

from t1_llm_api.base_client import AIClient


class BaseOpenAIClient(AIClient, ABC):
    """
    Abstract base class for OpenAI API clients.

    This class extends AIClient and adds OpenAI-specific initialization,
    particularly formatting the API key as a Bearer token for authorization.

    Attributes:
        Inherits all attributes from AIClient.
    """

    def __init__(self, endpoint: str, model_name: str, system_prompt: str, api_key: str):
        if not api_key or api_key.strip() == "":
            raise ValueError("API kay cannot be null or empty")

        super().__init__(
            endpoint = endpoint,
            model_name=model_name,
            api_key=f"Bearer {api_key}",
            system_prompt=system_prompt
        )