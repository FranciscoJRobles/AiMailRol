from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from api.models.scene import SceneStatus
from enum import Enum

class SceneBase(BaseModel):
    titulo: str
    descripcion_larga: str
    resumen_estado: str
    estado: SceneStatus

class SceneCreate(SceneBase):
    pass

class SceneUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion_larga: Optional[str] = None
    resumen_estado: Optional[str] = None
    estado: Optional[SceneStatus] = None

class SceneResponse(SceneBase):
    id: int
    fecha_inicio: datetime
    fecha_cierre: Optional[datetime]

    class Config:
        from_attributes = True

