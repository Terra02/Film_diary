from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ViewHistory(Base):
    __tablename__ = "view_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.id"), nullable=False)
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Float, nullable=True)
    duration_watched = Column(Integer, nullable=True)
    rewatch = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")
    content = relationship("Content")
    