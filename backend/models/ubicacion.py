from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    velocidad = Column(Float, default=0.0)  # km/h
    rumbo = Column("direccion", Float)
    altitud = Column(Float)                 # metros
    precision = Column(Float)               # metros
    # estado_motor = Column(Integer, default=0) 
    timestamp = Column("marca_tiempo", DateTime(timezone=True), server_default=func.now(), index=True)
    
    dispositivo = relationship("Dispositivo", back_populates="ubicaciones")
    
    def __repr__(self):
        return f"<Ubicacion(id={self.id}, lat={self.latitud}, lng={self.longitud})>"