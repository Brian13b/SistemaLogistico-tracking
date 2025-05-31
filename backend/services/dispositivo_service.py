from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.dispositivo import Dispositivo
from schemas.dispositivo_schema import DispositivoCreate, DispositivoUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

class DispositivoService:
    
    @staticmethod
    async def crear_dispositivo(db: AsyncSession, dispositivo_data: DispositivoCreate) -> Dispositivo:
        """Crear un nuevo dispositivo"""
        try:
            nuevo_dispositivo = Dispositivo(**dispositivo_data.model_dump())
            db.add(nuevo_dispositivo)
            await db.commit()
            await db.refresh(nuevo_dispositivo)
            logger.info(f"Dispositivo creado: {nuevo_dispositivo.serial_number}")
            return nuevo_dispositivo
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creando dispositivo: {e}")
            raise
    
    @staticmethod
    async def obtener_dispositivo_por_id(db: AsyncSession, dispositivo_id: str) -> Optional[Dispositivo]:
        """Obtener dispositivo por ID"""
        stmt = select(Dispositivo).where(Dispositivo.id == dispositivo_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def obtener_dispositivo_por_serial(db: AsyncSession, serial_number: str) -> Optional[Dispositivo]:
        """Obtener dispositivo por número de serie"""
        stmt = select(Dispositivo).where(Dispositivo.serial_number == serial_number)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def obtener_dispositivos(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        activos_solo: bool = True
    ) -> List[Dispositivo]:
        """Obtener lista de dispositivos"""
        stmt = select(Dispositivo)
        if activos_solo:
            stmt = stmt.where(Dispositivo.activo == True)
        stmt = stmt.offset(skip).limit(limit).order_by(Dispositivo.serial_number)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def obtener_dispositivos_por_vehiculo(db: AsyncSession, vehiculo_id: str) -> List[Dispositivo]:
        """Obtener dispositivos de un vehículo específico"""
        stmt = select(Dispositivo).where(
            Dispositivo.vehiculo_id == vehiculo_id,
            Dispositivo.activo == True
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def obtener_dispositivo_con_ubicaciones(
        db: AsyncSession, 
        dispositivo_id: str,
        limit_ubicaciones: int = 100
    ) -> Optional[Dispositivo]:
        """Obtener dispositivo con sus ubicaciones recientes"""
        stmt = select(Dispositivo).options(
            selectinload(Dispositivo.ubicaciones).limit(limit_ubicaciones)
        ).where(Dispositivo.id == dispositivo_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def actualizar_dispositivo(
        db: AsyncSession, 
        dispositivo_id: str, 
        dispositivo_data: DispositivoUpdate
    ) -> Optional[Dispositivo]:
        """Actualizar dispositivo"""
        try:
            # Filtrar solo campos no nulos
            update_data = {k: v for k, v in dispositivo_data.model_dump().items() if v is not None}
            if not update_data:
                return await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
            
            stmt = update(Dispositivo).where(Dispositivo.id == dispositivo_id).values(**update_data)
            await db.execute(stmt)
            await db.commit()
            
            return await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error actualizando dispositivo {dispositivo_id}: {e}")
            raise
    
    @staticmethod
    async def asignar_a_vehiculo(
        db: AsyncSession, 
        dispositivo_id: str, 
        vehiculo_id: str
    ) -> Optional[Dispositivo]:
        """Asignar dispositivo a un vehículo"""
        try:
            stmt = update(Dispositivo).where(
                Dispositivo.id == dispositivo_id
            ).values(vehiculo_id=vehiculo_id)
            await db.execute(stmt)
            await db.commit()
            
            return await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error asignando dispositivo {dispositivo_id} a vehículo {vehiculo_id}: {e}")
            raise
    
    @staticmethod
    async def desasignar_de_vehiculo(db: AsyncSession, dispositivo_id: str) -> Optional[Dispositivo]:
        """Desasignar dispositivo de un vehículo"""
        try:
            stmt = update(Dispositivo).where(
                Dispositivo.id == dispositivo_id
            ).values(vehiculo_id=None)
            await db.execute(stmt)
            await db.commit()
            
            return await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
        except Exception as e:
            await db.rollback()
            logger.error(f"Error desasignando dispositivo {dispositivo_id}: {e}")
            raise
    
    @staticmethod
    async def eliminar_dispositivo(db: AsyncSession, dispositivo_id: str) -> bool:
        """Eliminar dispositivo (soft delete)"""
        try:
            stmt = update(Dispositivo).where(Dispositivo.id == dispositivo_id).values(activo=False)
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            await db.rollback()
            logger.error(f"Error eliminando dispositivo {dispositivo_id}: {e}")
            raise