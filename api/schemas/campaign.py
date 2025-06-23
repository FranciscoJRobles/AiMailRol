from pydantic import BaseModel, field_serializer
from typing import Optional, List

class CampaignBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    nombre_clave: str
    resumen: Optional[str] = None
    character_ids: Optional[List[int]] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    nombre_clave: Optional[str] = None
    resumen: Optional[str] = None
    character_ids: Optional[List[int]] = None

class CampaignOut(CampaignBase):
    id: int
    story_state_ids: Optional[List[int]] = None

    @field_serializer('character_ids')
    def serialize_character_ids(self, value, info):
        # Si el objeto tiene la relación characters, devolver sus IDs
        if hasattr(self, 'characters') and self.characters is not None:
            return [c.id for c in self.characters]
        return value

    class Config:
        from_attributes = True
