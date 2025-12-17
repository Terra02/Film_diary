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
    rating = Column(Float, nullable=True)  # 1-10
    duration_watched = Column(Integer, nullable=True)  # в минутах
    rewatch = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User")
    content = relationship("Content")
    
    def __repr__(self):
        return f"<ViewHistory(id={self.id}, user_id={self.user_id}, content_id={self.content_id})>"
