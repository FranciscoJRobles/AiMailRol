from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum as SAEnum, func
from api.core.database import Base
from enum import Enum

class CharacterType(str, Enum):
    vampiro = "Vampiro"
    ghoul = "Ghoul"
    kueijin = "Kuei-Jin"
    hombrelobo = "HombreLobo"
    mago = "Mago"
    changeling = "Changeling"
    wraith = "Wraith"
    cazador = "Cazador"
    momia = "Momia"
    humano = "Humano"

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    nombre = Column(String, nullable=False)
    tipo = Column(SAEnum(CharacterType), nullable=False, index=True)
    hoja_json = Column(JSON, nullable=False)
    estado_actual = Column(JSON, nullable=False)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
