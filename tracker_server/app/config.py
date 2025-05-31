import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    TCP_HOST: str = os.getenv("TCP_HOST", "0.0.0.0")
    TCP_PORT: int = os.getenv("TCP_PORT", 5023)

    #BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/tracker/data")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "https://5ab2-181-230-133-18.ngrok-free.app/api/v1/tracker/data")

    ALLOWED_DEVICES: list = os.getenv("ALLOWED_DEVICES", "").split(",") if os.getenv("ALLOWED_DEVICES") else []
    #ALLOWED_DEVICES: list = os.getenv("ALLOWED_DEVICES", "").split(",")
    
    BACKEND_TIMEOUT: int = 5  # segundos
    
    NGROK_VERIFY_SSL: bool = os.getenv("NGROK_VERIFY_SSL", "false").lower() == "true"  # Para desarrollo puede ser False

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        
settings = Settings()