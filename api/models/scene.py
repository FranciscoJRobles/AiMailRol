from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, func, ForeignKey, Enum as PTEnum
from sqlalchemy.orm import relationship
from api.core.database import Base
from enum import Enum

class PhaseType(str, Enum):
    narracion = "narracion"
    combate = "combate"

class Scene(Base):
    __tablename__ = "scenes"
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    resumen = Column(Text, nullable=True)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    activa = Column(Boolean, default=True, nullable=False)  # Escena activa o no
    resumido = Column(Boolean, nullable=False, default=False)  # Indica si la escena(Scene) fue utilizada para generar un resumen
    fase_actual = Column(PTEnum(PhaseType), nullable=False, index=True)
    turns = relationship("Turn", back_populates="scene")
    story = relationship("Story", back_populates="scenes")
