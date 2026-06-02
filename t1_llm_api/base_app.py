from dotenv import load_dotenv

from commons.models.conversation import Conversation
from commons.models.message import Message
from commons.models.role import Role
from t1_llm_api.base_client import AIClient


load_dotenv()


async def start(stream: bool, client: AIClient) -> None:
    conversation = Conversation()

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        conversation.add_message(Message(role=Role.USER, content=user_input))

        if stream:
            response = await client.stream_response(conversation.messages)
        else:
            response = client.response(conversation.messages)

        conversation.add_message(response)
