from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from api.core.database import Base
from .associations import campaign_characters

class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    nombre_clave = Column(String, nullable=False, unique=True)
    resumen = Column(Text, nullable=True)
    activa = Column(Boolean, nullable=False, default=True)  # Nuevo campo para indicar si la campaña está activa
    characters = relationship("Character", secondary=campaign_characters, back_populates="campaigns")
    stories = relationship("Story", back_populates="campaign")
