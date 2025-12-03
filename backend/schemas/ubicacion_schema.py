from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UbicacionBase(BaseModel):
    dispositivo_id: int = Field(..., description="ID del dispositivo (PK de la base de datos)")
    latitud: float = Field(..., description="Latitud", ge=-90, le=90)
    longitud: float = Field(..., description="Longitud", ge=-180, le=180)
    velocidad: Optional[float] = Field(0.0, description="Velocidad en km/h", ge=0)
    rumbo: Optional[float] = Field(None, description="Rumbo en grados", ge=0, le=360)
    altitud: Optional[float] = Field(None, description="Altitud en metros")
    precision: Optional[float] = Field(None, description="Precisión en metros", ge=0)
    timestamp: Optional[datetime] = Field(None, description="Marca de tiempo de la ubicación")

class UbicacionCreate(UbicacionBase):
    pass

class UbicacionResponse(UbicacionBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class UbicacionTracker(BaseModel):
    device_id: str = Field(..., description="ID del dispositivo tracker (IMEI/Serial)")
    lat: float = Field(..., description="Latitud", ge=-90, le=90)
    lng: float = Field(..., description="Longitud", ge=-180, le=180)
    speed: Optional[float] = Field(0.0, description="Velocidad", ge=0)
    course: Optional[float] = Field(None, description="Rumbo", ge=0, le=360)
    altitude: Optional[float] = Field(None, description="Altitud")
    accuracy: Optional[float] = Field(None, description="Precisión", ge=0)
    timestamp: Optional[datetime] = None

class RutaResponse(BaseModel):
    dispositivo_id: int
    vehiculo_patente: Optional[str]
    ubicaciones: List[UbicacionResponse]
    total_puntos: int
    distancia_total: Optional[float] = None  
    tiempo_total: Optional[float] = None  