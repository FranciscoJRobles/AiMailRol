from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from api.core.database import Base
from .associations import story_characters

class Story(Base):
    __tablename__ = "stories"
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False, index=True)
    nombre = Column(Text, nullable=False)
    descripcion = Column(Text, nullable=True)
    resumen = Column(Text, nullable=True)
    tokens_est = Column(Integer, nullable=True)
    fecha_actualizacion = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    activa = Column(Boolean, nullable=False, default=True) 
    nombre_clave = Column(Text, nullable=False, unique=True, index=True)  # Unique keyword for Story
    characters = relationship("Character", secondary=story_characters, back_populates="stories")
    scenes = relationship("Scene", back_populates="story")
    campaign = relationship("Campaign", back_populates="stories")
