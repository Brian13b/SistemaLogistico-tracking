from .vehiculo_schema import VehiculoBase, VehiculoCreate, VehiculoUpdate, VehiculoResponse
from .dispositivo_schema import DispositivoBase, DispositivoCreate, DispositivoUpdate, DispositivoResponse
from .ubicacion_schema import UbicacionBase, UbicacionCreate, UbicacionResponse

__all__ = [
    "VehiculoBase", "VehiculoCreate", "VehiculoUpdate", "VehiculoResponse",
    "DispositivoBase", "DispositivoCreate", "DispositivoUpdate", "DispositivoResponse",
    "UbicacionBase", "UbicacionCreate", "UbicacionResponse"
]