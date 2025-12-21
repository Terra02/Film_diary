from typing import Optional, Dict, Any, List
from datetime import datetime
from app.services.api_client import api_client
from app.services.user_service import UserService

class HistoryService:
    def __init__(self):
        self.api_client = api_client
        self.user_service = UserService()

    async def get_user_history(
        self,
        telegram_id: int,
        limit: int = 10,
        profile: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        user = await self.user_service.get_or_create_user(
            telegram_id=telegram_id,
            username=(profile or {}).get("username"),
            first_name=(profile or {}).get("first_name"),
            last_name=(profile or {}).get("last_name"),
        )

        if not user:
            return []

        history = await self.api_client.get(
            f"/api/v1/view-history/user/{user['id']}?limit={limit}"
        )

        if not isinstance(history, list):
            return history

        def _parse_date(item: Dict[str, Any]):
            for key in ("watched_at", "created_at"):
                value = item.get(key)
                if isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value)
                    except ValueError:
                        continue
            return datetime.min

        return sorted(history, key=_parse_date, reverse=True)

    async def get_history_record(self, record_id: int) -> Optional[Dict[str, Any]]:
        return await self.api_client.get(f"/api/v1/view-history/{record_id}")

    async def ensure_content_exists(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        imdb_id = result.get("imdb_id")

        if imdb_id:
            existing = await self.api_client.get(f"/api/v1/content/imdb/{imdb_id}")
            if isinstance(existing, dict) and existing.get("id"):
                return existing

        title = result.get("title") or result.get("original_title")
        if not title:
            return None

        search_resp = await self.api_client.get(
            "/api/v1/content/search",
            params={"query": title, "limit": 1},
        )
        if isinstance(search_resp, dict) and search_resp.get("results"):
            first = search_resp["results"][0]
            if first and first.get("id"):
                return first

        payload = {
            "title": title,
            "original_title": result.get("original_title") or title,
            "description": result.get("description"),
            "content_type": result.get("content_type") or "movie",
            "release_year": result.get("release_year"),
            "imdb_rating": result.get("imdb_rating"),
            "imdb_id": imdb_id,
            "poster_url": result.get("poster_url"),
            "genre": result.get("genre"),
            "director": result.get("director"),
            "cast": result.get("cast"),
        }

        created = await self.api_client.post("/api/v1/content/", data=payload)
        if isinstance(created, dict) and created.get("id"):
            return created

        return None

    async def add_view_history(
        self,
        telegram_id: int,
        content_id: int,
        rating: Optional[float] = None,
        notes: Optional[str] = None,
        watched_at: Optional[datetime] = None,
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        profile = user_profile or {}
        user = await self.user_service.get_or_create_user(
            telegram_id=telegram_id,
            username=profile.get("username"),
            first_name=profile.get("first_name"),
            last_name=profile.get("last_name"),
        )

        if not user or not user.get("id"):
            return None

        history_data = {
            "user_id": user["id"],
            "content_id": content_id,
            "rating": rating,
            "notes": notes,
            "watched_at": watched_at.isoformat() if isinstance(watched_at, datetime) else watched_at,
        }

        created = await self.api_client.post("/api/v1/view-history/", data=history_data)

        if isinstance(created, dict) and created.get("id"):
            return created

        return None

    async def update_rating(self, record_id: int, rating: float) -> Optional[Dict[str, Any]]:
        return await self.api_client.put(
            f"/api/v1/view-history/{record_id}", data={"rating": rating}
        )