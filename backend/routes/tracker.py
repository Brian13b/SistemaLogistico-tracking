from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.ubicacion_service import UbicacionService
from schemas.ubicacion_schema import (
    UbicacionCreate, UbicacionResponse, UbicacionTracker, RutaResponse
)
from datetime import datetime, timedelta
from typing import List, Optional

router = APIRouter(prefix="/tracker", tags=["tracker"])

@router.post("/ubicacion", response_model=UbicacionResponse, status_code=201)
async def crear_ubicacion(ubicacion: UbicacionCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await UbicacionService.crear_ubicacion(db, ubicacion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error creando ubicación: {str(e)}")

@router.post("/data", response_model=UbicacionResponse, status_code=201)
async def recibir_datos_tracker(datos_tracker: UbicacionTracker, db: AsyncSession = Depends(get_db)):
    try:
        return await UbicacionService.procesar_datos_tracker(db, datos_tracker)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error procesando datos: {str(e)}")

@router.get("/dispositivo/{dispositivo_id}/actual", response_model=UbicacionResponse)
async def obtener_ubicacion_actual(dispositivo_id: str, db: AsyncSession = Depends(get_db)):
    ubicacion = await UbicacionService.obtener_ubicacion_actual(db, dispositivo_id)
    if not ubicacion:
        raise HTTPException(
            status_code=404, 
            detail="No se encontraron ubicaciones para este dispositivo"
        )
    return ubicacion

@router.get("/dispositivo/{dispositivo_id}/historial", response_model=List[UbicacionResponse])
async def obtener_historial_ubicaciones(
    dispositivo_id: str,
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    limit: int = Query(1000, ge=1, le=5000, description="Límite de registros"),
    db: AsyncSession = Depends(get_db)
):
    if not fecha_inicio and not fecha_fin:
        fecha_fin = datetime.utcnow()
        fecha_inicio = fecha_fin - timedelta(hours=24)
    
    ubicaciones = await UbicacionService.obtener_ubicaciones_por_dispositivo(
        db, dispositivo_id, fecha_inicio, fecha_fin, limit
    )
    
    if not ubicaciones:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron ubicaciones para el rango especificado"
        )
    
    return ubicaciones

@router.get("/vehiculo/{vehiculo_id}/recorrido", response_model=RutaResponse)
async def obtener_recorrido_vehiculo(
    vehiculo_id: str,
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio (ISO format)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin (ISO format)"),
    db: AsyncSession = Depends(get_db)
):  
    if not fecha_inicio and not fecha_fin:
        fecha_fin = datetime.utcnow()
        fecha_inicio = fecha_fin - timedelta(hours=24)
    
    recorrido = await UbicacionService.obtener_recorrido_vehiculo(
        db, vehiculo_id, fecha_inicio, fecha_fin
    )
    if not recorrido:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron ubicaciones para el vehículo en el rango especificado"
        )
    return recorrido

@router.get("/dispositivo/{dispositivo_id}/ultima-ubicacion", response_model=UbicacionResponse)
async def obtener_ultima_ubicacion(dispositivo_id: str, db: AsyncSession = Depends(get_db)):
    ubicacion = await UbicacionService.obtener_ultima_ubicacion(db, dispositivo_id)
    if not ubicacion:
        raise HTTPException(
            status_code=404,
            detail="No se encontró la última ubicación para este dispositivo"
        )
    return ubicacion