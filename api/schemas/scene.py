from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class SceneStatus(str, Enum):
    activa = "activa"
    finalizada = "finalizada"
    pausada = "pausada"

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
    fecha_cierre: Optional[datetime] = None

class SceneInDBBase(SceneBase):
    id: int
    fecha_inicio: datetime
    fecha_cierre: Optional[datetime]

    class Config:
        orm_mode = True

class SceneResponse(SceneInDBBase):
    pass
