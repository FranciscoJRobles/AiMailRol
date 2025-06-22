from pydantic import BaseModel
from typing import Any, Dict
from datetime import datetime
from api.models.character import CharacterType

class CharacterBase(BaseModel):
    player_id: int
    nombre: str
    tipo: CharacterType
    hoja_json: Dict[str, Any]
    estado_actual: Dict[str, Any]

class CharacterCreate(CharacterBase):
    pass

class CharacterOut(CharacterBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
