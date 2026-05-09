from typing import Any, List, Dict
from .base import BaseAWSAdapter

class IAMAdapter(BaseAWSAdapter):
    async def list_resources(self) -> List[Dict[str, Any]]:
        async with self.client_manager.get_client("iam") as client:
            response = await client.list_users()
            users = []
            for user in response.get("Users", []):
                users.append({
                    "username": user["UserName"],
                    "id": user["UserId"],
                    "created": user["CreateDate"].isoformat()
                })
            return users

    async def get_details(self, username: str) -> Dict[str, Any]:
        async with self.client_manager.get_client("iam") as client:
            response = await client.get_user(UserName=username)
            return response.get("User", {})
