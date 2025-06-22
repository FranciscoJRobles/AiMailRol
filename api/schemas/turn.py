from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any

class TurnBase(BaseModel):
    scene_id: int
    character_id: int
    orden_turno: int
    accion: str
    resolucion_ia: Optional[str] = None
    resultado_dado_json: Optional[Any] = None

class TurnCreate(TurnBase):
    pass

class TurnUpdate(BaseModel):
    accion: Optional[str] = None
    resolucion_ia: Optional[str] = None
    resultado_dado_json: Optional[Any] = None

class TurnOut(TurnBase):
    id: int
    fecha_envio: datetime

    class Config:
        from_attributes = True
