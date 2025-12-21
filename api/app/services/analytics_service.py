from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from typing import Dict, Any
from datetime import datetime, timedelta
import logging

from app.models.user import User
from app.models.content import Content
from app.models.view_history import ViewHistory

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_analytics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        total_views_stmt = select(func.count()).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at.between(start_date, end_date)
            )
        )
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        content_type_stmt = select(
            Content.content_type,
            func.count(ViewHistory.id)
        ).join(
            ViewHistory, Content.id == ViewHistory.content_id
        ).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.watched_at.between(start_date, end_date)
            )
        ).group_by(Content.content_type)

        content_type_result = await self.db.execute(content_type_stmt)
        content_type_stats = dict(content_type_result.all())

        avg_rating_stmt = select(func.avg(ViewHistory.rating)).where(
            and_(
                ViewHistory.user_id == user_id,
                ViewHistory.rating.isnot(None),
                ViewHistory.watched_at.between(start_date, end_date)
            )
        )
        avg_rating_result = await self.db.execute(avg_rating_stmt)
        avg_rating = round(avg_rating_result.scalar() or 0, 2)


        return {
            "total_views": total_views,
            "movies_views": content_type_stats.get('movie', 0),
            "series_views": content_type_stats.get('series', 0),
            "average_rating": avg_rating
        }

    async def get_user_timeline_analytics(self, user_id: int, period: str = "monthly") -> Dict[str, Any]:
        """Получить временную аналитику пользователя"""
        if period == "daily":
            group_by = "DATE(watched_at)"
        elif period == "weekly":
            group_by = "DATE_TRUNC('week', watched_at)"
        elif period == "yearly":
            group_by = "DATE_TRUNC('year', watched_at)"
        else: 
            group_by = "DATE_TRUNC('month', watched_at)"

        timeline_stmt = text(f"""
            SELECT 
                {group_by} as period,
                COUNT(*) as view_count,
                AVG(rating) as avg_rating
            FROM view_history 
            WHERE user_id = :user_id
            GROUP BY {group_by}
            ORDER BY period
        """)

        result = await self.db.execute(timeline_stmt, {"user_id": user_id})
        
        timeline_data = []
        for row in result:
            timeline_data.append({
                "view_count": row[1]
            })
        
        return {
            "period": period,
            "data": timeline_data
        }

    async def get_system_overview(self) -> Dict[str, Any]:
        total_users_stmt = select(func.count(User.id))
        total_users_result = await self.db.execute(total_users_stmt)
        total_users = total_users_result.scalar() or 0

        # Общее количество контента
        total_content_stmt = select(func.count(Content.id))
        total_content_result = await self.db.execute(total_content_stmt)
        total_content = total_content_result.scalar() or 0

        total_views_stmt = select(func.count(ViewHistory.id))
        total_views_result = await self.db.execute(total_views_stmt)
        total_views = total_views_result.scalar() or 0

        return {
            "total_users": total_users,
            "total_content": total_content,
            "total_views": total_views
        }