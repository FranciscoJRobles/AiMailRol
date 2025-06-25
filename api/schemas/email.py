from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from api.models.email import EmailType

class EmailBase(BaseModel):
    player_id: int
    character_id: int
    campaign_id: Optional[int] = None
    scene_id: Optional[int] = None  # Nuevo campo para asociar escena
    type: EmailType
    subject: str
    body: str
    sender: Optional[EmailStr] = None
    recipients: Optional[List[EmailStr]] = None
    thread_id: Optional[str] = ""
    message_id: Optional[str] = ""
    processed: Optional[bool] = False

class EmailCreate(EmailBase):
    pass 

class EmailOut(EmailBase):
    id: int
    date: datetime  # Solo en la respuesta
    class Config:
        from_attributes = True