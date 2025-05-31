from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database 
    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/tracking_db"
    TEST_DB_URL: Optional[str] = None
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Seguimiento Vehicular"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def database_url(self) -> str:
        """Retorna la URL de la base de datos"""
        if os.getenv("TESTING") == "1" and self.TEST_DB_URL:
            return self.TEST_DB_URL
        return self.DATABASE_URL  # Cambiado para usar DATABASE_URL
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        case_sensitive = True

settings = Settings()