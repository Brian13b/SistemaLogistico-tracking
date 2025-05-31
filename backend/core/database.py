from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# Crear engine con la configuración apropiada
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Base para los modelos
Base = declarative_base()
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency para obtener sesión de base de datos"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error en sesión de base de datos: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            await session.close()

async def init_db():
    """Inicializar base de datos"""
    async with engine.begin() as conn:
        # Importar todos los modelos para que SQLAlchemy los reconozca
        from models import vehiculo, dispositivo, ubicacion
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Base de datos inicializada correctamente")

async def close_db():
    """Cerrar conexiones de base de datos"""
    await engine.dispose()
    logger.info("Conexiones de base de datos cerradas")