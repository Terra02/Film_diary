from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ContentCreate(BaseModel):
    title: str
    original_title: Optional[str] = None
    description: Optional[str] = None
    content_type: str  
    release_year: Optional[int] = None
    imdb_rating: Optional[float] = None
    imdb_id: Optional[str] = None
    poster_url: Optional[str] = None
    genre: Optional[str] = None
    director: Optional[str] = None
    cast: Optional[str] = None


class ContentResponse(ContentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
