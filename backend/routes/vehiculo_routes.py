from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from services.vehiculo_service import VehiculoService
from schemas.vehiculo_schema import (
    VehiculoCreate, VehiculoUpdate, VehiculoResponse, VehiculoWithDispositivos
)
from typing import List

router = APIRouter(prefix="/vehiculos", tags=["vehiculos"])

@router.post("/", response_model=VehiculoResponse, status_code=201)
async def crear_vehiculo(
    vehiculo: VehiculoCreate,
    db: AsyncSession = Depends(get_db)
):
    """Crear un nuevo vehículo"""
    # Verificar si ya existe un vehículo con esa placa
    existing_vehiculo = await VehiculoService.obtener_vehiculo_por_placa(db, vehiculo.placa)
    if existing_vehiculo:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un vehículo con la placa {vehiculo.placa}"
        )
    
    return await VehiculoService.crear_vehiculo(db, vehiculo)

@router.get("/", response_model=List[VehiculoResponse])
async def listar_vehiculos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    activos_solo: bool = Query(True, description="Solo vehículos activos"),
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de vehículos"""
    return await VehiculoService.obtener_vehiculos(db, skip, limit, activos_solo)

@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener vehículo por ID"""
    vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.get("/{vehiculo_id}/completo", response_model=VehiculoWithDispositivos)
async def obtener_vehiculo_completo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener vehículo con sus dispositivos"""
    vehiculo = await VehiculoService.obtener_vehiculo_con_dispositivos(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.get("/placa/{placa}", response_model=VehiculoResponse)
async def obtener_vehiculo_por_placa(
    placa: str,
    db: AsyncSession = Depends(get_db)
):
    """Obtener vehículo por placa"""
    vehiculo = await VehiculoService.obtener_vehiculo_por_placa(db, placa)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
async def actualizar_vehiculo(
    vehiculo_id: str,
    vehiculo_update: VehiculoUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar vehículo"""
    # Verificar que el vehículo existe
    vehiculo_existente = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo_existente:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    # Si se está actualizando la placa, verificar que no exista otra igual
    if vehiculo_update.placa and vehiculo_update.placa != vehiculo_existente.placa:
        placa_existente = await VehiculoService.obtener_vehiculo_por_placa(db, vehiculo_update.placa)
        if placa_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un vehículo con la placa {vehiculo_update.placa}"
            )
    
    vehiculo_actualizado = await VehiculoService.actualizar_vehiculo(db, vehiculo_id, vehiculo_update)
    if not vehiculo_actualizado:
        raise HTTPException(status_code=404, detail="Error actualizando vehículo")
    
    return vehiculo_actualizado

@router.delete("/{vehiculo_id}")
async def eliminar_vehiculo(
    vehiculo_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Eliminar vehículo (soft delete)"""
    eliminado = await VehiculoService.eliminar_vehiculo(db, vehiculo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return {"message": "Vehículo eliminado correctamente"}