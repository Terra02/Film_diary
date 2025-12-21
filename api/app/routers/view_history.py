from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.view_history import (ViewHistoryResponse, ViewHistoryCreate,ViewHistoryWithContent)
from app.services.view_history_service import ViewHistoryService

router = APIRouter(prefix="/view-history", tags=["view-history"])

#для получения истории просмотра
@router.get("/user/{user_id}", response_model=List[ViewHistoryWithContent])
async def get_user_view_history(user_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100), 
                                db: AsyncSession = Depends(get_db)
):
    history_service = ViewHistoryService(db)
    history = await history_service.get_user_view_history_with_content(user_id, skip, limit)
    return history

#для внесения в список просмотренного
@router.post("/", response_model=ViewHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_view_history(history_data: ViewHistoryCreate, db: AsyncSession = Depends(get_db)):
    history_service = ViewHistoryService(db)
    history = await history_service.create_view_history(history_data)
    return history

#получение статистики
@router.get("/user/{user_id}/stats")
async def get_user_stats(user_id: int, db: AsyncSession = Depends(get_db)):
    history_service = ViewHistoryService(db)
    stats = await history_service.get_user_stats(user_id)
    return stats