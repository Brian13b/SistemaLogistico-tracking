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
async def crear_vehiculo(vehiculo: VehiculoCreate, db: AsyncSession = Depends(get_db)):
    existing_vehiculo = await VehiculoService.obtener_vehiculo_por_patente(db, vehiculo.patente)
    if existing_vehiculo:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un vehículo con la patente {vehiculo.patente}"
        )
    
    return await VehiculoService.crear_vehiculo(db, vehiculo)

@router.get("/", response_model=List[VehiculoResponse])
async def listar_vehiculos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Límite de registros"),
    activos_solo: bool = Query(True, description="Solo vehículos activos"),
    db: AsyncSession = Depends(get_db)
):
    return await VehiculoService.obtener_vehiculos(db, skip, limit, activos_solo)

@router.get("/{vehiculo_id}", response_model=VehiculoResponse)
async def obtener_vehiculo(vehiculo_id: str, db: AsyncSession = Depends(get_db)):
    vehiculo = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.get("/{vehiculo_id}/completo", response_model=VehiculoWithDispositivos)
async def obtener_vehiculo_completo(vehiculo_id: str, db: AsyncSession = Depends(get_db)):
    vehiculo = await VehiculoService.obtener_vehiculo_con_dispositivos(db, vehiculo_id)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.get("/patente/{patente}", response_model=VehiculoResponse)
async def obtener_vehiculo_por_patente(patente: str, db: AsyncSession = Depends(get_db)):
    vehiculo = await VehiculoService.obtener_vehiculo_por_patente(db, patente)
    if not vehiculo:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return vehiculo

@router.put("/{vehiculo_id}", response_model=VehiculoResponse)
async def actualizar_vehiculo(vehiculo_id: str, vehiculo_update: VehiculoUpdate, db: AsyncSession = Depends(get_db)):
    vehiculo_existente = await VehiculoService.obtener_vehiculo_por_id(db, vehiculo_id)
    if not vehiculo_existente:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    if vehiculo_update.patente and vehiculo_update.patente != vehiculo_existente.patente:
        patente_existente = await VehiculoService.obtener_vehiculo_por_patente(db, vehiculo_update.patente)
        if patente_existente:
            raise HTTPException(
                status_code=400,
                detail=f"Ya existe un vehículo con la patente {vehiculo_update.patente}"
            )
    
    vehiculo_actualizado = await VehiculoService.actualizar_vehiculo(db, vehiculo_id, vehiculo_update)
    if not vehiculo_actualizado:
        raise HTTPException(status_code=404, detail="Error actualizando vehículo")
    
    return vehiculo_actualizado

@router.delete("/{vehiculo_id}")
async def eliminar_vehiculo(vehiculo_id: str, db: AsyncSession = Depends(get_db)):
    eliminado = await VehiculoService.eliminar_vehiculo(db, vehiculo_id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    
    return {"message": "Vehículo eliminado correctamente"}