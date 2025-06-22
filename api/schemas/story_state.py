from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StoryStateBase(BaseModel):
    scene_id: int
    contenido_resumido: str
    tokens_est: int

class StoryStateCreate(StoryStateBase):
    pass

class StoryStateUpdate(BaseModel):
    contenido_resumido: Optional[str] = None
    tokens_est: Optional[int] = None

class StoryStateOut(StoryStateBase):
    id: int
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True
