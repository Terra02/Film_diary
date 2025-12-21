from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

#нужен для получения вычисления аналитики
@router.get("/user/{user_id}")
async def get_user_analytics(user_id: int, days: Optional[int] = Query(30, ge=1, le=365), db: AsyncSession = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    analytics = await analytics_service.get_user_analytics(user_id, start_date, end_date)
    return analytics

#для получения статистики за периол
@router.get("/user/{user_id}/timeline")
async def get_user_timeline_analytics( user_id: int, period: str = Query("daily", regex="^(daily|weekly|monthly|yearly)$"),
                                      db: AsyncSession = Depends(get_db)
):
    analytics_service = AnalyticsService(db)
    timeline_data = await analytics_service.get_user_timeline_analytics(user_id, period)
    return timeline_data

#общая инфа по системе
@router.get("/system/overview")
async def get_system_overview(db: AsyncSession = Depends(get_db)):
    analytics_service = AnalyticsService(db)
    overview = await analytics_service.get_system_overview()
    return overview