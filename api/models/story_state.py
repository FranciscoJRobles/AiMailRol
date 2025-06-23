from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from api.core.database import Base
from .associations import story_state_characters

class StoryState(Base):
    __tablename__ = "story_states"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    contenido_resumido = Column(Text, nullable=True)
    tokens_est = Column(Integer, nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    characters = relationship("Character", secondary=story_state_characters, back_populates="story_states")
    scenes = relationship("Scene", back_populates="story_state")
    campaign = relationship("Campaign", back_populates="story_states")
