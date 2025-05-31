from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class VehiculoBase(BaseModel):
    placa: str = Field(..., description="Placa del vehículo", max_length=10)
    marca: Optional[str] = Field(None, description="Marca del vehículo", max_length=50)
    modelo: Optional[str] = Field(None, description="Modelo del vehículo", max_length=50)
    year: Optional[str] = Field(None, description="Año del vehículo", max_length=4)
    activo: bool = Field(True, description="Estado del vehículo")

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(BaseModel):
    placa: Optional[str] = Field(None, max_length=10)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=50)
    year: Optional[str] = Field(None, max_length=4)
    activo: Optional[bool] = None

class VehiculoResponse(VehiculoBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VehiculoWithDispositivos(VehiculoResponse):
    dispositivos: List['DispositivoResponse'] = []
    
    class Config:
        from_attributes = True

# Para evitar circular imports
from .dispositivo_schema import DispositivoResponse
VehiculoWithDispositivos.model_rebuild()