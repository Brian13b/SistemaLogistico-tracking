from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import uuid

class Dispositivo(Base):
    __tablename__ = "dispositivos"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    imei = Column(String, unique=True, nullable=False, index=True)
    modelo = Column(String, default="CY06")
    vehiculo_id = Column(String, ForeignKey("vehiculos.id"), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    vehiculo = relationship("Vehiculo", back_populates="dispositivos")
    ubicaciones = relationship("Ubicacion", back_populates="dispositivo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dispositivo(id={self.id}, imei={self.imei})>"