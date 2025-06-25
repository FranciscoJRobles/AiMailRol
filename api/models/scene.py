from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from api.core.database import Base

class Scene(Base):
    __tablename__ = "scenes"
    id = Column(Integer, primary_key=True, index=True)
    story_state_id = Column(Integer, ForeignKey("story_states.id"), nullable=False, index=True)
    titulo = Column(String, nullable=False)
    descripcion_larga = Column(Text, nullable=False)
    resumen_estado = Column(Text, nullable=False)
    fecha_inicio = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    fecha_cierre = Column(DateTime(timezone=True), nullable=True)
    activa = Column(Boolean, default=True, nullable=False)  # Escena activa o no
    turns = relationship("Turn", back_populates="scene")
    story_state = relationship("StoryState", back_populates="scenes")
