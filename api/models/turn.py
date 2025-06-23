from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from api.core.database import Base

class Turn(Base):
    __tablename__ = "turns"
    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"), nullable=False, index=True)
    orden_turno = Column(Integer, nullable=False)
    accion = Column(Text, nullable=False)
    resolucion_ia = Column(Text, nullable=True)
    fecha_envio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resultado_dado_json = Column(JSON, nullable=True)
    scene = relationship("Scene", back_populates="turns")
