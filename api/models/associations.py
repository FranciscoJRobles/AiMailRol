from sqlalchemy import Table, Column, Integer, ForeignKey
from api.core.database import Base

campaign_characters = Table(
    "campaign_characters",
    Base.metadata,
    Column("campaign_id", Integer, ForeignKey("campaigns.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True)
)

story_state_characters = Table(
    "story_state_characters",
    Base.metadata,
    Column("story_state_id", Integer, ForeignKey("story_states.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True)
)
