from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Dispositivo(Base):
    __tablename__ = "dispositivos"
    
    # CAMBIO: Usamos Integer para coincidir con la DB (SERIAL)
    id = Column(Integer, primary_key=True, index=True) 
    
    imei = Column(String, unique=True, nullable=False, index=True)
    marca = Column(String)  # Agregué marca porque estaba en tu SQL
    modelo = Column(String, default="CY06")
    firmware_version = Column(String) # Agregado según tu SQL
    activo = Column(Boolean, default=True)
    created_at = Column("creado_en", DateTime(timezone=True), server_default=func.now())
    last_seen = Column("ultima_vez_visto", DateTime(timezone=True)) 
    
    ubicaciones = relationship("Ubicacion", back_populates="dispositivo", cascade="all, delete-orphan")
    vehiculo = relationship("Vehiculo", back_populates="dispositivo", uselist=False)

    def __repr__(self):
        return f"<Dispositivo(id={self.id}, imei={self.imei})>"