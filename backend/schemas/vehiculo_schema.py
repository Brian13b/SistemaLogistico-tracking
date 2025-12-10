from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, ForwardRef

DispositivoResponse = ForwardRef('DispositivoResponse')

class VehiculoBase(BaseModel):
    patente: str = Field(..., description="Patente del vehículo", max_length=10)
    marca: Optional[str] = Field(None, description="Marca del vehículo", max_length=50)
    modelo: Optional[str] = Field(None, description="Modelo del vehículo", max_length=50)
    year: Optional[int] = Field(None, description="Año del vehículo")
    tipo_motor: Optional[str] = Field(None, description="Tipo de motor")
    capacidad_combustible: Optional[float] = Field(None, description="Capacidad de combustible")
    tipo_vehiculo: Optional[str] = Field(None, description="Tipo de vehículo")
    odometro_inicial: Optional[float] = Field(None, description="Odómetro inicial")
    velocidad_maxima_permitida: Optional[float] = Field(None, description="Velocidad máxima permitida")
    activo: bool = Field(True, description="Estado del vehículo")

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(BaseModel):
    patente: Optional[str] = Field(None, max_length=10)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    year: Optional[int] = Field(None)
    tipo_motor: Optional[str] = Field(None)
    capacidad_combustible: Optional[float] = Field(None)
    tipo_vehiculo: Optional[str] = Field(None)
    odometro_inicial: Optional[float] = Field(None)
    velocidad_maxima_permitida: Optional[float] = Field(None)
    activo: Optional[bool] = None

class VehiculoResponse(VehiculoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VehiculoWithDispositivos(VehiculoResponse):
    dispositivos: List[DispositivoResponse] = []
    
    class Config:
        from_attributes = True

from .dispositivo_schema import DispositivoResponse
VehiculoWithDispositivos.model_rebuild()