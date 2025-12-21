from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    original_title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=False) 
    release_year = Column(Integer, nullable=True)
    imdb_rating = Column(Float, nullable=True)
    imdb_id = Column(String(20), unique=True, nullable=True)
    poster_url = Column(String(500), nullable=True)
    genre = Column(String(255), nullable=True)
    director = Column(String(255), nullable=True)
    actors_cast = Column(Text, nullable=True)
    language = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    view_history = relationship("ViewHistory")
    watchlists = relationship("Watchlist")
