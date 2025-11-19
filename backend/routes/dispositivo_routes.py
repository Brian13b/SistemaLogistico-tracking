from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.dispositivo_service import DispositivoService
from services.vehiculo_service import VehiculoService
from schemas.dispositivo_schema import (
    DispositivoCreate, DispositivoUpdate, DispositivoResponse, DispositivoWithUbicaciones
)
from typing import List

router = APIRouter(prefix="/dispositivos", tags=["dispositivos"])

@router.post("/", response_model=DispositivoResponse, status_code=201)
async def crear_dispositivo(
    dispositivo: DispositivoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo dispositivo"""
    
    # Verificar si ya existe un dispositivo con ese imei
    existing_dispositivo = await DispositivoService.obtener_dispositivo_por_imei(
        db, dispositivo.imei
    )
    if existing_dispositivo:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un dispositivo con el IMEI {dispositivo.imei}"
        )
    
    # Si se asigna a un vehículo, verificar que exista
    if dispositivo.vehiculo_id:
        vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, dispositivo.vehiculo_id)
        if not vehiculo:
            raise HTTPException(
                status_code=400,
                detail=f"El vehículo con ID {dispositivo.vehiculo_id} no existe"
            )
    
    return await DispositivoService.crear_dispositivo(db, dispositivo)

@router.get("/", response_model=List[DispositivoResponse])
async def listar_dispositivos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    activos_solo: bool = Query(True, description="Solo dispositivos activos"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de dispositivos"""
    return await DispositivoService.obtener_dispositivos(db, skip, limit, activos_solo)

@router.get("/{dispositivo_id}", response_model=DispositivoResponse)
async def obtener_dispositivo(
    dispositivo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener dispositivo por ID"""
    dispositivo = await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@router.get("/{dispositivo_id}/completo", response_model=DispositivoWithUbicaciones)
async def obtener_dispositivo_completo(
    dispositivo_id: str,
    limit_ubicaciones: int = Query(100, ge=1, le=1000, description="Límite de ubicaciones"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener dispositivo con sus ubicaciones recientes"""
    dispositivo = await DispositivoService.obtener_dispositivo_con_ubicaciones(
        db, dispositivo_id, limit_ubicaciones
    )
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@router.get("/imei/{imei}", response_model=DispositivoResponse)
async def obtener_dispositivo_por_imei(
    imei_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener dispositivo por número de serie"""
    dispositivo = await DispositivoService.obtener_dispositivo_por_imei(db, imei)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    return dispositivo

@router.get("/vehiculo/{vehiculo_id}", response_model=List[DispositivoResponse])
async def obtener_dispositivos_por_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener dispositivos de un vehículo específico"""
    # Verificar que el vehículo existe
    vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return await DispositivoService.obtener_dispositivos_por_vehiculo(db, vehiculo_id)

@router.put("/{dispositivo_id}", response_model=DispositivoResponse)
async def actualizar_dispositivo(
    dispositivo_id: str,
    dispositivo_update: DispositivoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar dispositivo"""
    # Verificar que el dispositivo existe
    dispositivo_existente = await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
    if not dispositivo_existente:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    # Si se está actualizando el imei, verificar que no exista otro igual
    if (dispositivo_update.imei and 
        dispositivo_update.imei != dispositivo_existente.imei):
        imei_existente = await DispositivoService.obtener_dispositivo_por_imei(
            db, dispositivo_update.imei
        )
        if imei_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un dispositivo con el imei {dispositivo_update.imei}"
            )
    
    # Si se está asignando a un vehículo, verificar que exista
    if dispositivo_update.vehiculo_id:
        vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, dispositivo_update.vehiculo_id)
        if not vehiculo:
            raise HTTPException(
                status_code=400,
                detail=f"El vehículo con ID {dispositivo_update.vehiculo_id} no existe"
            )
    
    dispositivo_actualizado = await DispositivoService.actualizar_dispositivo(
        db, dispositivo_id, dispositivo_update
    )
    if not dispositivo_actualizado:
        raise HTTPException(status_code=404, detail="Error actualizando dispositivo")
    
    return dispositivo_actualizado

@router.post("/{dispositivo_id}/asignar/{vehiculo_id}", response_model=DispositivoResponse)
async def asignar_dispositivo_a_vehiculo(
    dispositivo_id: str,
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Asignar dispositivo a un vehículo"""
    # Verificar que ambos existen
    dispositivo = await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return await DispositivoService.asignar_a_vehiculo(db, dispositivo_id, vehiculo_id)

@router.post("/{dispositivo_id}/desasignar", response_model=DispositivoResponse)
async def desasignar_dispositivo(
    dispositivo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Desasignar dispositivo de su vehículo actual"""
    dispositivo = await DispositivoService.obtener_dispositivo_por_id(db, dispositivo_id)
    if not dispositivo:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    return await DispositivoService.desasignar_de_vehiculo(db, dispositivo_id)

@router.delete("/{dispositivo_id}")
async def eliminar_dispositivo(
    dispositivo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar dispositivo (soft delete)"""
    eliminado = await DispositivoService.eliminar_dispositivo(db, dispositivo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Dispositivo no encontrado")
    
    return {"message": "Dispositivo eliminado correctamente"}