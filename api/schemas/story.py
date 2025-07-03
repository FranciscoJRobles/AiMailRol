from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import datetime

class StoryBase(BaseModel):
    campaign_id: int
    nombre: str
    descripcion: Optional[str] = None
    contenido_resumido: Optional[str] = None
    tokens_est: Optional[int] = None
    activa: bool = True
    character_ids: Optional[List[int]] = None
    scene_ids: Optional[List[int]] = None

class StoryCreate(StoryBase):
    pass

class StoryUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

class StoryOut(StoryBase):
    id: int
    fecha_actualizacion: datetime

    @field_serializer('character_ids')
    def serialize_character_ids(self, value, info):
        if hasattr(self, 'characters') and self.characters is not None:
            return [c.id for c in self.characters]
        return value

    class Config:
        from_attributes = True