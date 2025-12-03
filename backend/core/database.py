from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from core.config import settings
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

original_url = settings.get_database_url()

if original_url and original_url.startswith("postgres://"):
    database_url = original_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif original_url and original_url.startswith("postgresql://"):
    database_url = original_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    database_url = original_url

if "?" in database_url:
    database_url = database_url.split("?")[0]

engine = create_async_engine(
    database_url, 
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"ssl": "require"}
)

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Error en sesión de base de datos: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        try:
            from models import vehiculo, dispositivo, ubicacion
        except ImportError:
             pass
             
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Base de datos inicializada correctamente")

async def close_db():
    await engine.dispose()
    logger.info("Conexiones de base de datos cerradas")