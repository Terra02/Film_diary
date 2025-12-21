from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = Field(..., validation_alias="DATABASE_URL")
    
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    omdb_api_key: Optional[str] = None
    
    search_external_timeout: int = 10
    max_external_results: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()