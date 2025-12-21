from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.view_history import ViewHistory
from app.models.content import Content
from app.schemas.view_history import ViewHistoryCreate

logger = logging.getLogger(__name__)

class ViewHistoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_view_history_by_id(self, history_id: int) -> Optional[ViewHistory]:
        result = await self.db.execute(
            select(ViewHistory).where(ViewHistory.id == history_id)
        )
        return result.scalar_one_or_none()

    async def create_view_history(self, history_data: ViewHistoryCreate) -> ViewHistory:
        history = ViewHistory(**history_data.model_dump())
        self.db.add(history)
        try:
            await self.db.commit()
            await self.db.refresh(history)
            logger.info(f"Создана запись просмотра для  {history_data.user_id}")
            return history
        except IntegrityError as exc:
            await self.db.rollback()

            if "unique_view_record" in str(getattr(exc, "orig", exc)).lower():
                existing_stmt = select(ViewHistory).where(
                    and_(
                        ViewHistory.user_id == history_data.user_id,
                        ViewHistory.content_id == history_data.content_id,
                        ViewHistory.watched_at == history_data.watched_at,
                    )
                )
                existing_result = await self.db.execute(existing_stmt)
                existing = existing_result.scalar_one_or_none()

                if existing:
                    update_data = history_data.model_dump(
                        exclude_none=True,
                        exclude={"user_id", "content_id"},
                    )

                    for field, value in update_data.items():
                        setattr(existing, field, value)

                    await self.db.commit()
                    await self.db.refresh(existing)
                    logger.info(
                        "Обновлена запись просмотра для пользователя %s и контента %s",
                        history_data.user_id,
                        history_data.content_id,
                    )
                    return existing

            raise

    async def get_user_view_history_with_content(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        result = await self.db.execute(
            select(ViewHistory, Content)
            .join(Content, ViewHistory.content_id == Content.id)
            .where(ViewHistory.user_id == user_id)
            .order_by(
                desc(ViewHistory.watched_at),
                desc(ViewHistory.created_at)
            )
            .offset(skip)
            .limit(limit)
        )

        history_with_content = []
        for history, content in result:
            content_dict = {
                column.key: getattr(content, column.key)
                for column in Content.__table__.columns
            }

            history_dict = {
                **{column.key: getattr(history, column.key) for column in ViewHistory.__table__.columns},
                "id": history.id,
                "created_at": history.created_at,
                "content_title": content.title,
                "content_type": content.content_type,
                "content": content_dict,
            }
            history_with_content.append(history_dict)

        return history_with_content

    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        total_views_stmt = select(func.count()).where(ViewHistory.user_id == user_id)
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        movies_views_stmt = select(func.count()).select_from(ViewHistory).join(Content).where(
            and_(ViewHistory.user_id == user_id, Content.content_type == 'movie')
        )
        movies_views_result = await self.db.execute(movies_views_stmt)
        movies_views = movies_views_result.scalar() or 0

        series_views_stmt = select(func.count()).select_from(ViewHistory).join(Content).where(
            and_(ViewHistory.user_id == user_id, Content.content_type == 'series')
        )
        series_views_result = await self.db.execute(series_views_stmt)
        series_views = series_views_result.scalar() or 0

        avg_rating_stmt = select(func.avg(ViewHistory.rating)).where(
            and_(ViewHistory.user_id == user_id, ViewHistory.rating.isnot(None))
        )
        avg_rating_result = await self.db.execute(avg_rating_stmt)
        avg_rating = round(avg_rating_result.scalar() or 0, 2)

        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_views_stmt = select(func.count()).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at >= thirty_days_ago
            )
        )
        recent_views_result = await self.db.execute(recent_views_stmt)
        recent_views = recent_views_result.scalar() or 0

        return {
            "total_views": total_views,
            "movies_views": movies_views,
            "series_views": series_views,
            "average_rating": avg_rating,
            "recent_views_30_days": recent_views
        }
