from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import init_db
from routes import (
    tracker,
    vehiculo_routes as vehiculos,
    dispositivo_routes as dispositivos
)
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
env_path = Path(__file__).resolve().parents[1] / '.env'
load_dotenv(env_path)

app = FastAPI(
    title="Sistema de Seguimiento Vehicular",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS (ajustar según necesidades)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(tracker.router, prefix="/api/v1")
app.include_router(vehiculos.router, prefix="/api/v1")
app.include_router(dispositivos.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Inicializar base de datos al arrancar"""
    try:
        await init_db()
        logger.info("Aplicación iniciada correctamente")
    except Exception as e:
        logger.error(f"Error al iniciar la aplicación: {e}")
        raise

@app.get("/api/health", tags=["health"])
async def health_check():
    """Endpoint de verificación de salud"""
    return {"status": "ok"}