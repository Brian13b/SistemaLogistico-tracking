from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import uuid

class Vehiculo(Base):
    __tablename__ = "vehiculos"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    placa = Column(String, unique=True, nullable=False, index=True)
    marca = Column(String)
    modelo = Column(String)
    year = Column(String)
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relaciones
    dispositivos = relationship("Dispositivo", back_populates="vehiculo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Vehiculo(id={self.id}, placa={self.placa})>"