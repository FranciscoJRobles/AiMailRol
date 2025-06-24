from sqlalchemy import Column, Integer, String, Boolean, ARRAY, DateTime, func, Enum as SAEnum, ForeignKey
from api.core.database import Base
from enum import Enum

class EmailType(str, Enum):
    ENTRADA = "HumanEntry"
    RESPUESTA = "IAResponse"


class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, index=True)
    character_id = Column(Integer, index=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'), index=True, nullable=True)  # Nuevo campo para asociar campaña
    type = Column(SAEnum(EmailType), nullable=False, index=True)  # Ahora usa Enum SQLAlchemy
    subject = Column(String, nullable=False)
    body = Column(String)
    sender = Column(String, default="")
    recipients = Column(ARRAY(String))  # Solo compatible con PostgreSQL
    thread_id = Column(String, nullable=False, default="")
    message_id = Column(String, nullable=False, default="")
    date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    processed = Column(Boolean, nullable=False, default=False)

    def set_type(self, value):
        if isinstance(value, EmailType):
            self.type = value.value
        elif value in EmailType._value2member_map_:
            self.type = value
        else:
            raise ValueError(f"type debe ser uno de: {[e.value for e in EmailType]}")