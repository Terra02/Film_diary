from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.watchlist import (WatchlistResponse, WatchlistCreate, WatchlistWithContent)
from app.services.watchlist_service import WatchlistService

router = APIRouter(prefix="/watchlist", tags=["watchlist"])
#передает вочлист пользователя
@router.get("/user/{user_id}", response_model=List[WatchlistWithContent])
async def get_user_watchlist(user_id: int, skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=100),db: AsyncSession = Depends(get_db)):
    watchlist_service = WatchlistService(db)
    watchlist = await watchlist_service.get_user_watchlist_with_content(user_id, skip, limit)
    return watchlist

#добавляем запись в вочлист
@router.post("/", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED) 
async def add_to_watchlist(item_data: WatchlistCreate, db: AsyncSession = Depends(get_db)):
    watchlist_service = WatchlistService(db)
    try:
        item = await watchlist_service.create_watchlist(item_data)
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

#удаляем из вочлиста
@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(watchlist_id: int, db: AsyncSession = Depends(get_db)):
    watchlist_service = WatchlistService(db)
    success = await watchlist_service.delete_watchlist(watchlist_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )
    
#очищаем вочлист полностью
@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_user_watchlist(user_id: int, db: AsyncSession = Depends(get_db)):
    watchlist_service = WatchlistService(db)
    await watchlist_service.clear_user_watchlist(user_id)
