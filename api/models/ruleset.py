from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey
from api.core.database import Base

class Ruleset(Base):
    __tablename__ = "rulesets"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(Text, nullable=False)
    reglas_json = Column(JSON, nullable=False)
    ambientacion_json = Column(JSON, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
