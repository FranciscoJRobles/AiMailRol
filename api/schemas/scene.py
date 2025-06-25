from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SceneBase(BaseModel):
    story_state_id: int
    titulo: str
    descripcion_larga: str
    resumen_estado: str
    activa: bool = True  # Nuevo campo para indicar si la escena está activa

class SceneCreate(SceneBase):
    pass

class SceneUpdate(BaseModel):
    story_state_id: Optional[int] = None
    titulo: Optional[str] = None
    descripcion_larga: Optional[str] = None
    resumen_estado: Optional[str] = None
    activa: Optional[bool] = None  # Actualización de activa

class SceneResponse(SceneBase):
    id: int
    fecha_inicio: datetime
    fecha_cierre: Optional[datetime]

    class Config:
        from_attributes = True

