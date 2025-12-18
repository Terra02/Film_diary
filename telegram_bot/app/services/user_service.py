from typing import Optional
from app.services.api_client import api_client

class UserService:
    def __init__(self):
        self.api_client = api_client

    async def get_or_create_user(self, telegram_id: int, username: Optional[str] = None,
                               first_name: Optional[str] = None, last_name: Optional[str] = None):

        user_data = await self.api_client.get(f"/api/v1/users/telegram/{telegram_id}")
        if isinstance(user_data, dict) and user_data.get("id"):
            return user_data

        new_user = {
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name
        }

        created = await self.api_client.post("/api/v1/users/", data=new_user)

        if isinstance(created, dict) and created.get("id"):
            return created

        return None

    async def get_user(self, user_id: int):
        return await self.api_client.get(f"/api/v1/users/{user_id}")

    async def update_user(self, user_id: int, user_data: dict):
        return await self.api_client.put(f"/api/v1/users/{user_id}", data=user_data)