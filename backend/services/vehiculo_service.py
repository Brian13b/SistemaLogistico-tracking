from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.vehiculo import Vehiculo
from schemas.vehiculo_schema import VehiculoCreate, VehiculoUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class VehiculoService:
    
    @staticmethod
    async def crear_vehiculo(db: AsyncSession, vehiculo_data: VehiculoCreate) -> Vehiculo:
        """Crear un nuevo vehículo"""
        try:
            nuevo_vehiculo = Vehiculo(**vehiculo_data.model_dump())
            db.add(nuevo_vehiculo)
            await db.commit()
            await db.refresh(nuevo_vehiculo)
            logger.info(f"Vehículo creado: {nuevo_vehiculo.patente}")
            return nuevo_vehiculo
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creando vehículo: {e}")
            raise
    
    @staticmethod
    async def obtener_vehiculo_por_id(db: AsyncSession, vehiculo_id: str) -> Optional[Vehiculo]:
        """Obtener vehículo por ID"""
        stmt = select(Vehiculo).where(Vehiculo.id == vehiculo_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def obtener_vehiculo_por_patente(db: AsyncSession, patente: str) -> Optional[Vehiculo]:
        """Obtener vehículo por patente"""
        stmt = select(Vehiculo).where(Vehiculo.patente == patente)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def obtener_vehiculos(db: AsyncSession, skip: int = 0, limit: int = 100,activos_solo: bool = True) -> List[Vehiculo]:
        """Obtener lista de vehículos"""
        stmt = select(Vehiculo)
        if activos_solo:
            stmt = stmt.where(Vehiculo.activo == True)
        stmt = stmt.offset(skip).limit(limit).order_by(Vehiculo.patente)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def obtener_vehiculo_con_dispositivos(db: AsyncSession, vehiculo_id: str) -> Optional[Vehiculo]:
        """Obtener vehículo con sus dispositivos"""
        stmt = select(Vehiculo).options(
            selectinload(Vehiculo.dispositivos)
        ).where(Vehiculo.id == vehiculo_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def actualizar_vehiculo(db: AsyncSession, vehiculo_id: str, vehiculo_data: VehiculoUpdate) -> Optional[Vehiculo]:
        """Actualizar vehículo"""
        try:
            update_data = {k: v for k, v in vehiculo_data.model_dump().items() if v is not None}
            if not update_data:
                return await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
            
            stmt = update(Vehiculo).where(Vehiculo.id == vehiculo_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            
            return await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error actualizando vehículo {vehiculo_id}: {e}")
            raise
    
    @staticmethod
    async def eliminar_vehiculo(db: AsyncSession, vehiculo_id: str) -> bool:
        """Eliminar vehículo (soft delete)"""
        try:
            stmt = update(Vehiculo).where(Vehiculo.id == vehiculo_id).values(activo=False)
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            await db.rollback()
            logger.error(f"Error eliminando vehículo {vehiculo_id}: {e}")
            raise