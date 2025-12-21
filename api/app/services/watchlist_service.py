from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from typing import Optional, List, Dict, Any
import logging

from app.models.watchlist import Watchlist
from app.models.content import Content
from app.schemas.watchlist import WatchlistCreate

logger = logging.getLogger(__name__)

class WatchlistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_watchlist_by_id(self, watchlist_id: int) -> Optional[Watchlist]:
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.id == watchlist_id)
        )
        return result.scalar_one_or_none()

    async def create_watchlist(self, watchlist_data: WatchlistCreate) -> Watchlist:
        existing = await self.db.execute(
            select(Watchlist).where(
                and_(
                    Watchlist.user_id == watchlist_data.user_id,
                    Watchlist.content_id == watchlist_data.content_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Контент уже в watchlist")

        watchlist = Watchlist(**watchlist_data.model_dump())
        self.db.add(watchlist)
        await self.db.commit()
        await self.db.refresh(watchlist)
        logger.info(f"Добавлен контент {watchlist_data.content_id} для пользователя {watchlist_data.user_id}  в watchlist")
        return watchlist

    async def delete_watchlist(self, watchlist_id: int) -> bool:
        watchlist = await self.get_watchlist_by_id(watchlist_id)
        if not watchlist:
            return False

        await self.db.delete(watchlist)
        await self.db.commit()
        logger.info(f"Удалено из watchlist: {watchlist_id}")
        return True

    async def clear_user_watchlist(self, user_id: int) -> None:
        result = await self.db.execute(
            select(Watchlist).where(Watchlist.user_id == user_id)
        )
        items = result.scalars().all()
        for item in items:
            await self.db.delete(item)
        await self.db.commit()
        logger.info(f"Очищен watchlist для {user_id}")


    async def get_user_watchlist_with_content(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        result = await self.db.execute(
            select(Watchlist, Content)
            .join(Content, Watchlist.content_id == Content.id)
            .where(Watchlist.user_id == user_id)
            .order_by(desc(Watchlist.added_at))
            .offset(skip)
            .limit(limit)
        )

        watchlist_with_content = []
        for watchlist, content in result:
            content_dict = {
                column.key: getattr(content, column.key)
                for column in Content.__table__.columns
            }

            watchlist_dict = {
                **{column.key: getattr(watchlist, column.key) for column in Watchlist.__table__.columns},
                "id": watchlist.id,
                "added_at": watchlist.added_at,
                "content_title": content.title,
                "content_type": content.content_type,
                "content": content_dict,
            }
            watchlist_with_content.append(watchlist_dict)

        return watchlist_with_content
