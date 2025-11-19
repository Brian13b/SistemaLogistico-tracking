from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, ForwardRef

UbicacionResponse = ForwardRef('UbicacionResponse')

class DispositivoBase(BaseModel):
    imei: str = Field(..., description="Número de serie del dispositivo", max_length=50)
    modelo: str = Field("CY06", description="Modelo del dispositivo")
    vehiculo_id: Optional[int] = Field(None, description="ID del vehículo asociado")
    activo: bool = Field(True, description="Estado del dispositivo")

class DispositivoCreate(DispositivoBase):
    pass

class DispositivoUpdate(BaseModel):
    imei: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None)
    vehiculo_id: Optional[int] = None
    activo: Optional[bool] = None

class DispositivoResponse(DispositivoBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DispositivoWithUbicaciones(DispositivoResponse):
    ubicaciones: List[UbicacionResponse] = []
    
    class Config:
        from_attributes = True

from .ubicacion_schema import UbicacionResponse
DispositivoWithUbicaciones.model_rebuild()