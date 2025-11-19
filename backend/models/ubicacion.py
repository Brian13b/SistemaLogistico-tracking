from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import uuid

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    dispositivo_id = Column(String, ForeignKey("dispositivos.id"), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    velocidad = Column(Float, default=0.0)  # km/h
    rumbo = Column("direccion", Float)  # grados (0-360)
    altitud = Column(Float)  # metros
    precision = Column(Float)  # metros
    #estado_motor = Column(Integer, default=0)  # 0: apagado, 1: encendido
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="ubicaciones")
    
    def __repr__(self):
        return f"<Ubicacion(id={self.id}, lat={self.latitud}, lng={self.longitud})>"