from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Watchlist(Base):
    __tablename__ = "watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    user = relationship("User")
    content = relationship("Content")
    