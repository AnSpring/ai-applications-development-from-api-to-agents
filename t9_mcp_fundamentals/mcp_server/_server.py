from pathlib import Path

from mcp.server.fastmcp import FastMCP

from commons.user_service.client import UserServiceClient
from commons.user_service.user_info import UserSearchRequest, UserCreate, UserUpdate

# 1. FastMCP instance
mcp = FastMCP(
    name="users-management-mcp-server",
    host="0.0.0.0",
    port=8005,
)

# 2. UserServiceClient instance
user_service_client = UserServiceClient()


# ==================== TOOLS ====================

@mcp.tool(description="Get user by ID from the User Service")
async def get_user_by_id(user_id: int) -> str:
    return user_service_client.get_user(user_id)


@mcp.tool(description="Delete user by ID from the User Service")
async def delete_user(user_id: int) -> str:
    return user_service_client.delete_user(user_id)


@mcp.tool(description="Search users by name, surname, email or gender")
async def search_user(
        name: str | None = None,
        surname: str | None = None,
        email: str | None = None,
        gender: str | None = None
) -> str:
    return user_service_client.search_users(
        name=name,
        surname=surname,
        email=email,
        gender=gender
    )


@mcp.tool(description="Add a new user to the User Service")
async def add_user(user: UserCreate) -> str:
    return user_service_client.add_user(user)


@mcp.tool(description="Update an existing user by ID in the User Service")
async def update_user(user_id: int, user: UserUpdate) -> str:
    return user_service_client.update_user(user_id, user)


# ==================== MCP RESOURCES ====================

@mcp.resource(
    uri="users-management://flow-diagram",
    mime_type="image/png",
    description="Screenshot with Swagger endpoints of User Service"
)
async def get_flow_diagram() -> bytes:
    flow_path = Path(__file__).parent.parent / "flow.png"
    return flow_path.read_bytes()


# ==================== MCP PROMPTS ====================

@mcp.prompt(description="Guide for searching users in the database")
async def search_users_guide() -> str:
    return """
You are helping users search through a dynamic user database...
(первый большой текст из файла)
"""


@mcp.prompt(description="Guide for creating realistic user profiles")
async def create_user_guide() -> str:
    return """
You are helping create realistic user profiles for the system...
(второй большой текст из файла)
"""