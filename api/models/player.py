from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, func
from api.core.database import Base
from enum import Enum

class PlayerStatus(str, Enum):
    activo = "Activo"
    inactivo = "Inactivo"
    baneado = "Baneado"

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    nickname = Column(String(32), unique=True, nullable=False)
    fecha_registro = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    estado = Column(SAEnum(PlayerStatus), default=PlayerStatus.activo, nullable=False)
