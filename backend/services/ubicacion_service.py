from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from models.ubicacion import Ubicacion
from models.dispositivo import Dispositivo
from models.vehiculo import Vehiculo
from schemas.ubicacion_schema import UbicacionCreate, UbicacionResponse, UbicacionTracker, RutaResponse
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict
import logging
import math

logger = logging.getLogger(__name__)

class UbicacionService:
    
    @staticmethod
    async def crear_ubicacion(db: AsyncSession, ubicacion_data: UbicacionCreate) -> Ubicacion:
        """Crear una nueva ubicación"""
        try:
            data = ubicacion_data.model_dump()

            if not data.get("timestamp"):
                data["timestamp"] = datetime.now(timezone.utc)

            nueva_ubicacion = Ubicacion(**data)

            db.add(nueva_ubicacion)
            await db.commit()
            await db.refresh(nueva_ubicacion)
            logger.info(f"Ubicación creada para dispositivo: {nueva_ubicacion.dispositivo_id}")
            return nueva_ubicacion
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creando ubicación: {e}")
            raise
    
    @staticmethod
    async def procesar_datos_tracker(db: AsyncSession, datos_tracker: UbicacionTracker) -> Ubicacion:
        """Procesar datos del tracker y crear ubicación"""
        try:
            stmt = select(Dispositivo).where(Dispositivo.imei == datos_tracker.device_id)
            result = await db.execute(stmt)
            dispositivo = result.scalar_one_or_none()
            
            if not dispositivo:
                logger.warning(f"⚠️ IMEI desconocido intentando reportar: {datos_tracker.device_id}")
                raise ValueError(f"Dispositivo {datos_tracker.device_id} no encontrado")
            
            dispositivo.last_seen = datos_tracker.timestamp or datetime.now(timezone.utc)
            
            stmt_last = select(Ubicacion).where(
                Ubicacion.dispositivo_id == dispositivo.id
            ).order_by(desc(Ubicacion.timestamp)).limit(1)
            
            last_location = (await db.execute(stmt_last)).scalar_one_or_none()
            
            guardar_nuevo = True
            
            if last_location:
                distancia_km = UbicacionService._calcular_distancia_puntos(
                    last_location.latitud, last_location.longitud,
                    datos_tracker.lat, datos_tracker.lng
                )
                tiempo_diff_seg = (datos_tracker.timestamp - last_location.timestamp).total_seconds()
                
                if distancia_km < 0.03 and tiempo_diff_seg < 300:
                    
                    if datos_tracker.speed == 0 and last_location.velocidad > 0:
                        guardar_nuevo = True
                        logger.info(f"🛑 Vehículo {dispositivo.imei} se detuvo. Guardando evento.")
                    else:
                        guardar_nuevo = False

            if guardar_nuevo:
                ubicacion_data = UbicacionCreate(
                    dispositivo_id=dispositivo.id,
                    latitud=datos_tracker.lat,
                    longitud=datos_tracker.lng,
                    velocidad=datos_tracker.speed or 0.0,
                    rumbo=datos_tracker.course,
                    altitud=datos_tracker.altitude,
                    precision=datos_tracker.accuracy,
                    timestamp=datos_tracker.timestamp
                )
                nueva_ubicacion = await UbicacionService.crear_ubicacion(db, ubicacion_data)
                
                await db.commit() 
                return nueva_ubicacion
            else:
                await db.commit()
                return last_location

        except Exception as e:
            logger.error(f"Error procesando datos del tracker: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def obtener_ubicacion_actual(db: AsyncSession, dispositivo_id: str) -> Optional[Ubicacion]:
        """Obtener la ubicación más reciente de un dispositivo"""
        dispositivo_id_int = int(dispositivo_id)

        stmt = select(Ubicacion).where(
            Ubicacion.dispositivo_id == dispositivo_id_int
        ).order_by(desc(Ubicacion.timestamp)).limit(1)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def obtener_ubicaciones_por_dispositivo(db: AsyncSession, dispositivo_id: str, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None, limit: int = 1000) -> List[Ubicacion]:
        """Obtener ubicaciones de un dispositivo en un rango de fechas"""
        dispositivo_id_int = int(dispositivo_id)
        
        stmt = select(Ubicacion).where(Ubicacion.dispositivo_id == dispositivo_id_int)
        
        if fecha_inicio:
            stmt = stmt.where(Ubicacion.timestamp >= fecha_inicio)
        if fecha_fin:
            stmt = stmt.where(Ubicacion.timestamp <= fecha_fin)
        
        stmt = stmt.order_by(desc(Ubicacion.timestamp)).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def obtener_recorrido_vehiculo(db: AsyncSession, vehiculo_id: str, fecha_inicio: Optional[datetime] = None, fecha_fin: Optional[datetime] = None) -> Optional[RutaResponse]:
        """Obtener el recorrido completo de un vehículo"""
        try:
            vehiculo_stmt = select(Vehiculo).options(
                selectinload(Vehiculo.dispositivos)
            ).where(Vehiculo.id == vehiculo_id)
            vehiculo_result = await db.execute(vehiculo_stmt)
            vehiculo = vehiculo_result.scalar_one_or_none()
            
            if not vehiculo or not vehiculo.dispositivos:
                return None
            
            dispositivos_ids = [d.id for d in vehiculo.dispositivos if d.activo]
            if not dispositivos_ids:
                return None
            
            stmt = select(Ubicacion).where(Ubicacion.dispositivo_id.in_(dispositivos_ids))
            
            if fecha_inicio:
                stmt = stmt.where(Ubicacion.timestamp >= fecha_inicio)
            if fecha_fin:
                stmt = stmt.where(Ubicacion.timestamp <= fecha_fin)
            
            stmt = stmt.order_by(Ubicacion.timestamp)
            result = await db.execute(stmt)
            ubicaciones = result.scalars().all()
            
            distancia_total = UbicacionService._calcular_distancia_recorrido(ubicaciones)
            tiempo_total = UbicacionService._calcular_tiempo_recorrido(ubicaciones)
            
            return RutaResponse(
                dispositivo_id=dispositivos_ids[0] if dispositivos_ids else "",
                vehiculo_patente=vehiculo.patente,
                ubicaciones=ubicaciones,
                total_puntos=len(ubicaciones),
                distancia_total=distancia_total,
                tiempo_total=tiempo_total
            )
        except Exception as e:
            logger.error(f"Error obteniendo recorrido del vehículo {vehiculo_id}: {e}")
            raise
    
    @staticmethod
    async def obtener_ubicaciones_tiempo_real(db: AsyncSession, minutos_atras: int = 5) -> List[Dict]:
        """Obtener ubicaciones recientes para monitoreo en tiempo real"""
        try:
            tiempo_limite = datetime.now(timezone.utc) - timedelta(minutes=minutos_atras)
            
            subquery = select(
                Ubicacion.dispositivo_id,
                func.max(Ubicacion.timestamp).label('max_timestamp')
            ).where(
                Ubicacion.timestamp >= tiempo_limite
            ).group_by(Ubicacion.dispositivo_id).subquery()
            
            stmt = select(
                Ubicacion,
                Dispositivo.imei,
                Vehiculo.patente
            ).select_from(
                Ubicacion.join(
                    subquery,
                    and_(
                        Ubicacion.dispositivo_id == subquery.c.dispositivo_id,
                        Ubicacion.timestamp == subquery.c.max_timestamp
                    )
                ).join(Dispositivo).outerjoin(Vehiculo)
            ).where(Dispositivo.activo == True)
            
            result = await db.execute(stmt)
            ubicaciones_tiempo_real = []
            
            for ubicacion, imei, patente in result:
                ubicacion_data = UbicacionResponse.model_validate(ubicacion).model_dump()
                
                ubicaciones_tiempo_real.append({
                    "ubicacion": ubicacion_data, 
                    "dispositivo_imei": imei,
                    "vehiculo_patente": patente
                })
            
            return ubicaciones_tiempo_real
            
        except Exception as e:
            logger.error(f"Error obteniendo ubicaciones en tiempo real: {e}")
            raise
    
    @staticmethod
    def _calcular_distancia_recorrido(ubicaciones: List[Ubicacion]) -> Optional[float]:
        """Calcular distancia total del recorrido usando fórmula de Haversine"""
        if len(ubicaciones) < 2:
            return None
        
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calcular distancia entre dos puntos en la Tierra"""
            R = 6371  # Radio de la Tierra en km
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = (math.sin(dlat/2) * math.sin(dlat/2) + 
                 math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
                 math.sin(dlon/2) * math.sin(dlon/2))
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c
        
        distancia_total = 0
        for i in range(1, len(ubicaciones)):
            dist = haversine_distance(
                ubicaciones[i-1].latitud, ubicaciones[i-1].longitud,
                ubicaciones[i].latitud, ubicaciones[i].longitud
            )
            distancia_total += dist
        
        return round(distancia_total, 2)
    
    @staticmethod
    def _calcular_tiempo_recorrido(ubicaciones: List[Ubicacion]) -> Optional[float]:
        """Calcular tiempo total del recorrido en minutos"""
        if len(ubicaciones) < 2:
            return None
        
        tiempo_inicio = ubicaciones[0].timestamp
        tiempo_fin = ubicaciones[-1].timestamp
        diferencia = tiempo_fin - tiempo_inicio
        
        return round(diferencia.total_seconds() / 60, 2)
    
    @staticmethod
    def _calcular_distancia_puntos(lat1, lon1, lat2, lon2):
        """Calcula distancia Haversine entre dos puntos (retorna KM)"""
        import math
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c