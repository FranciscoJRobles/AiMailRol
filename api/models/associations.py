from sqlalchemy import Table, Column, Integer, ForeignKey
from api.core.database import Base

campaign_characters = Table(
    "campaign_characters",
    Base.metadata,
    Column("campaign_id", Integer, ForeignKey("campaigns.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True)
)

story_characters = Table(
    "story_characters",
    Base.metadata,
    Column("story_id", Integer, ForeignKey("stories.id"), primary_key=True),
    Column("character_id", Integer, ForeignKey("characters.id"), primary_key=True)
)
