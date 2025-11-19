import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Configuración del servidor TCP
    TCP_HOST: str = os.getenv("TCP_HOST", "0.0.0.0")
    TCP_PORT: int = int(os.getenv("TCP_PORT", 5023))
    
    # Configuración del backend
    BACKEND_URL_TRACKING: str = os.getenv("BACKEND_URL_TRACKING", "https://sistemalogistico-tracking.onrender.com:8002/api/v1/tracker/data")
    API_KEY: str = os.getenv("API_KEY", "")
    BACKEND_TIMEOUT: int = int(os.getenv("BACKEND_TIMEOUT", 5))
    
    # Dispositivos permitidos
    ALLOWED_DEVICES: list = [
        dev.strip() for dev in os.getenv("ALLOWED_DEVICES", "").split(",") 
        if dev.strip()
    ]
    
    # Configuración adicional
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BUFFER_SIZE: int = int(os.getenv("BUFFER_SIZE", 1024))

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        
settings = Settings()