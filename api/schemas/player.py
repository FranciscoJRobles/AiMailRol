from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from api.models.player import PlayerStatus


class PlayerBase(BaseModel):
    email: EmailStr
    nickname: str = Field(min_length=3, max_length=32)
    estado: PlayerStatus = PlayerStatus.activo
    
class PlayerCreate(PlayerBase):
    pass

class PlayerOut(PlayerBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True