from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WatchlistCreate(BaseModel):
    user_id: int
    content_id: int
    notes: Optional[str] = None

class WatchlistResponse(WatchlistCreate):
    id: int
    added_at: datetime
    content_title: Optional[str] = None
    content_type: Optional[str] = None
    class Config:
        from_attributes = True

class WatchlistWithContent(WatchlistResponse):
    content: Optional[dict] = None