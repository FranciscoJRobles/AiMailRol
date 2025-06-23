from pydantic import BaseModel
from typing import Any, Dict, Optional, List
from datetime import datetime
from api.models.character import CharacterType

class CharacterBase(BaseModel):
    player_id: int
    nombre: str
    tipo: CharacterType
    hoja_json: Dict[str, Any]
    estado_actual: Dict[str, Any]
    activo: bool
    campaign_ids: Optional[List[int]] = None
    story_state_ids: Optional[List[int]] = None

class CharacterCreate(BaseModel):
    player_id: int
    nombre: str
    tipo: CharacterType
    hoja_json: Dict[str, Any]
    estado_actual: Dict[str, Any]
    activo: bool

class CharacterUpdate(BaseModel):
    player_id: Optional[int] = None
    nombre: Optional[str] = None
    tipo: Optional[CharacterType] = None
    hoja_json: Optional[Dict[str, Any]] = None
    estado_actual: Optional[Dict[str, Any]] = None
    activo: Optional[bool] = None
    campaign_ids: Optional[List[int]] = None
    story_state_ids: Optional[List[int]] = None

class CharacterOut(CharacterBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True
