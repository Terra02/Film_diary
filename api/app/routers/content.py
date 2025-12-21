from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.content import ContentResponse, ContentCreate
from app.services.content_service import ContentService

router = APIRouter(prefix="/content", tags=["content"])

#для проверки в бд контента при ensure_content_exists
@router.get("/imdb/{imdb_id}", response_model=ContentResponse)
async def get_content_by_imdb_id(imdb_id: str, db: AsyncSession = Depends(get_db)):
    content_service = ContentService(db)
    content = await content_service.get_content_by_imdb_id(imdb_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Уонтент не найден"
        )
    return content

#для добавлениея в бд контента при ensure_content_exists
@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(content_data: ContentCreate, db: AsyncSession = Depends(get_db)):
    content_service = ContentService(db)
    content = await content_service.create_content(content_data)
    return content

