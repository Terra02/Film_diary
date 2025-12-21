from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, field_validator

def _validate_watched_at(value: Optional[datetime]) -> Optional[datetime]:
    if value is None:
        return value

    min_allowed_date = date(2020, 1, 1)
    if value.date() < min_allowed_date:
        raise ValueError("Дата просмотра не может быть раньше 01.01.2020")

    now = datetime.now(tz=value.tzinfo) if value.tzinfo else datetime.now()
    if value > now:
        raise ValueError("Дата просмотра не может быть в будущем")

    return value

class ViewHistoryBase(BaseModel):
    user_id: int
    content_id: int
    watched_at: Optional[datetime] = None
    rating: Optional[float] = None
    duration_watched: Optional[int] = None
    notes: Optional[str] = None


class ViewHistoryCreate(ViewHistoryBase):
    @field_validator("watched_at")
    @classmethod
    def validate_watched_at(cls, value: Optional[datetime]) -> Optional[datetime]:
        return _validate_watched_at(value)


class ViewHistoryResponse(ViewHistoryBase):
    id: int
    watched_at: datetime
    created_at: datetime
    content_title: Optional[str] = None
    content_type: Optional[str] = None

    class Config:
        from_attributes = True


class ViewHistoryWithContent(ViewHistoryResponse):
    content: Optional[dict] = None
