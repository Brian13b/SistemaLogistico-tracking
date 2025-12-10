from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    
    id = Column(Integer, primary_key=True, index=True)
    patente = Column(String, unique=True, nullable=False, index=True)
    marca = Column(String)
    modelo = Column(String)
    year = Column("año", Integer) 
    tipo_motor = Column(String)
    capacidad_combustible = Column(Float)
    tipo_vehiculo = Column(String)
    odometro_inicial = Column(Float)
    velocidad_maxima_permitida = Column(Float)
    activo = Column(Boolean, default=True)
    created_at = Column("creado_en", DateTime(timezone=True), server_default=func.now())
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)

    dispositivo = relationship("Dispositivo", back_populates="vehiculo")

    def __repr__(self):
        return f"<Vehiculo(id={self.id}, patente={self.patente})>"