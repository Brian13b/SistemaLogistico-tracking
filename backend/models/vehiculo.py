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
    tipo_vehiculo = Column(String)
    activo = Column(Boolean, default=True)
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    created_at = Column("creado_en", DateTime(timezone=True), server_default=func.now())

    dispositivo = relationship("Dispositivo", back_populates="vehiculo")

    def __repr__(self):
        return f"<Vehiculo(id={self.id}, patente={self.patente})>"