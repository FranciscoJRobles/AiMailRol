from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from api.core.database import Base

class StoryState(Base):
    __tablename__ = "story_states"
    id = Column(Integer, primary_key=True, index=True)
    scene_id = Column(Integer, ForeignKey("scenes.id"), nullable=False, index=True)
    contenido_resumido = Column(Text, nullable=False)
    tokens_est = Column(Integer, nullable=False)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
