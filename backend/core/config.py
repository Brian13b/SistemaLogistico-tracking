from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database 
    URL_DATABASE: str = os.getenv("DATABASE_URL")
    TEST_DB_URL: Optional[str] = None
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Seguimiento Vehicular"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    def get_database_url(self) -> str:
        if os.getenv("TESTING") == "1" and self.TEST_DB_URL:
            return self.TEST_DB_URL
        return self.URL_DATABASE
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()