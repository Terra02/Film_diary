from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.services.content_service import ContentService

router = APIRouter(prefix="/bot", tags=["bot"])
#для поиска
@router.get("/search")
async def bot_search_content(title: str, content_type: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    content_service = ContentService(db)
    result = await content_service.search_omdb_direct(title, content_type)
    
    if result["source"] == "not_found":
        raise HTTPException(
            status_code=404,
            detail=result["message"]
        )
    
    return result
#логика поиска 1+4 в search_omdb_direct