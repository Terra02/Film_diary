from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    telegram_id: str = Field(..., description="Telegram ID пользователя")
    username: Optional[str] = Field(None, max_length=50, description="Имя пользователя в Telegram")
    first_name: Optional[str] = Field(None, max_length=100, description="Имя пользователя")
    last_name: Optional[str] = Field(None, max_length=100, description="Фамилия пользователя")
    

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True