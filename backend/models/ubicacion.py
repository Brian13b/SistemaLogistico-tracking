from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    
    # 1. CAMBIO CRÍTICO: Integer para coincidir con SERIAL de Postgres
    # Quitamos el default de UUID para que la DB asigne el número automáticamente
    id = Column(Integer, primary_key=True, index=True)
    
    # 2. CAMBIO: Integer para la llave foránea
    dispositivo_id = Column(Integer, ForeignKey("dispositivos.id"), nullable=False)
    
    latitud = Column(Float, nullable=False)
    longitud = Column(Float, nullable=False)
    velocidad = Column(Float, default=0.0)  # km/h
    
    # 3. Mapeo de columnas (Nombre en Python -> Nombre en Base de Datos)
    rumbo = Column("direccion", Float)      # En Python 'rumbo', en DB 'direccion'
    altitud = Column(Float)                 # metros
    precision = Column(Float)               # metros
    
    # (Opcional) Si quieres guardar estado_motor, descomenta y asegúrate de crear la columna en la DB
    # estado_motor = Column(Integer, default=0) 
    
    # 4. CAMBIO: Mapear 'timestamp' a 'marca_tiempo'
    # Si no haces esto, SQLAlchemy buscará una columna 'timestamp' que no existe
    timestamp = Column("marca_tiempo", DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relaciones
    dispositivo = relationship("Dispositivo", back_populates="ubicaciones")
    
    def __repr__(self):
        return f"<Ubicacion(id={self.id}, lat={self.latitud}, lng={self.longitud})>"