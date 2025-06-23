from pydantic import BaseModel, field_serializer
from datetime import datetime
from typing import Optional, List

class StoryStateBase(BaseModel):
    campaign_id: int
    nombre: str
    descripcion: Optional[str] = None
    contenido_resumido: Optional[str] = None
    tokens_est: Optional[int] = None
    character_ids: Optional[List[int]] = None  # IDs de personajes asociados
    scene_ids: Optional[List[int]] = None      # IDs de escenas asociadas

class StoryStateCreate(StoryStateBase):
    pass

class StoryStateUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    contenido_resumido: Optional[str] = None
    tokens_est: Optional[int] = None
    character_ids: Optional[List[int]] = None
    scene_ids: Optional[List[int]] = None

class StoryStateOut(StoryStateBase):
    id: int
    fecha_actualizacion: datetime

    @field_serializer('character_ids')
    def serialize_character_ids(self, value, info):
        if hasattr(self, 'characters') and self.characters is not None:
            return [c.id for c in self.characters]
        return value

    class Config:
        from_attributes = True
