from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DispositivoBase(BaseModel):
    serial_number: str = Field(..., description="Número de serie del dispositivo", max_length=50)
    modelo: str = Field("CY06", description="Modelo del dispositivo")
    vehiculo_id: Optional[str] = Field(None, description="ID del vehículo asociado")
    activo: bool = Field(True, description="Estado del dispositivo")

class DispositivoCreate(DispositivoBase):
    pass

class DispositivoUpdate(BaseModel):
    serial_number: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None)
    vehiculo_id: Optional[str] = None
    activo: Optional[bool] = None

class DispositivoResponse(DispositivoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DispositivoWithUbicaciones(DispositivoResponse):
    ubicaciones: List['UbicacionResponse'] = []
    
    class Config:
        from_attributes = True

# Para evitar circular imports
from .ubicacion_schema import UbicacionResponse
DispositivoWithUbicaciones.model_rebuild()