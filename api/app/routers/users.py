from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
from app.schemas.user import UserResponse, UserBase
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])
#для получения пользов. по id (для аналитики)
@router.get("/telegram/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram(telegram_id: int,db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user

#для создания пользователя
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserBase,db: AsyncSession = Depends(get_db)):
    service = UserService(db)
        
    user = await service.create_user(user_data)
    return user

