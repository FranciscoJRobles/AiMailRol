from sqlalchemy.orm import Session
from api.models.campaign import Campaign
from api.models.character import Character
from api.models.story_state import StoryState
from api.schemas.campaign import CampaignCreate

class CampaignCRUD:
    @staticmethod
    def add_character_to_campaign(db: Session, campaign_id: int, character_id: int):
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        character = db.query(Character).filter(Character.id == character_id).first()
        if campaign and character:
            campaign.characters.append(character)
            db.commit()
            db.refresh(campaign)
        return campaign

    @staticmethod
    def remove_character_from_campaign(db: Session, campaign_id: int, character_id: int):
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        character = db.query(Character).filter(Character.id == character_id).first()
        if campaign and character and character in campaign.characters:
            campaign.characters.remove(character)
            db.commit()
            db.refresh(campaign)
        return campaign

    @staticmethod
    def get_campaign_story_states(db: Session, campaign_id: int):
        return db.query(StoryState).filter(StoryState.campaign_id == campaign_id).all()

    @staticmethod
    def get_active_campaign_keywords(db: Session):
        """
        Devuelve una lista de todas las palabras clave (nombre_clave) de campañas activas.
        """
        return [c.nombre_clave for c in db.query(Campaign).filter(Campaign.activa == True).all()]

    @staticmethod
    def get_characters_by_campaign_id(db: Session, campaign_id: int):
        """
        Devuelve una lista con los nombres de los personajes asociados a una campaña.
        """
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.characters:
            return [character.nombre for character in campaign.characters]
        return []
