from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    API_URL: str = "http://api:8000"
    API_PREFIX: str = "/api/v1"  
    class Config:
        env_file = ".env"

settings = Settings()