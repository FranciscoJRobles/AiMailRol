from sqlalchemy.orm import Session
from api.models.campaign import Campaign
from api.models.character import Character
from api.models.story import Story
from api.schemas.campaign import CampaignCreate, CampaignUpdate

class CampaignManager:
    @staticmethod
    def create_campaign(db: Session, campaign: CampaignCreate):
        db_campaign = Campaign(
            nombre=campaign.nombre,
            descripcion=campaign.descripcion,
            nombre_clave=campaign.nombre_clave,
            resumen=campaign.resumen
        )
        if campaign.character_ids:
            db_campaign.characters = db.query(Character).filter(Character.id.in_(campaign.character_ids)).all()
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def get_campaigns(db: Session, skip: int = 0, limit: int = 100):
        return db.query(Campaign).offset(skip).limit(limit).all()

    @staticmethod
    def get_campaign(db: Session, campaign_id: int):
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    @staticmethod
    def update_campaign(db: Session, campaign_id: int, campaign_update: CampaignUpdate):
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return None
        for field, value in campaign_update.model_dump(exclude_unset=True).items():
            if field == "character_ids":
                # Comprobar que todos los IDs existen
                characters = db.query(Character).filter(Character.id.in_(value)).all()
                if len(characters) != len(value):
                    raise ValueError("Uno o más character_ids no existen")
                db_campaign.characters = characters
            else:
                setattr(db_campaign, field, value)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: int):
        db_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not db_campaign:
            return False
        db.delete(db_campaign)
        db.commit()
        return True

    @staticmethod
    def add_character_to_campaign(db: Session, campaign_id: int, character_id: int):
        """Añade un personaje a una campaña"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        character = db.query(Character).filter(Character.id == character_id).first()
        if campaign and character:
            campaign.characters.append(character)
            db.commit()
            db.refresh(campaign)
        return campaign

    @staticmethod
    def remove_character_from_campaign(db: Session, campaign_id: int, character_id: int):
        """Remueve un personaje de una campaña"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        character = db.query(Character).filter(Character.id == character_id).first()
        if campaign and character and character in campaign.characters:
            campaign.characters.remove(character)
            db.commit()
            db.refresh(campaign)
        return campaign

    @staticmethod
    def get_campaign_stories(db: Session, campaign_id: int):
        """Obtiene todas las historias de una campaña"""
        return db.query(Story).filter(Story.campaign_id == campaign_id).all()

    @staticmethod
    def get_characters_by_campaign_id(db: Session, campaign_id: int):
        """Devuelve una lista con los nombres de los personajes asociados a una campaña"""
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if campaign and campaign.characters:
            return [character.nombre for character in campaign.characters]
        return []

    @staticmethod
    def get_campaign_by_keyword(db: Session, keyword: str) -> Campaign:
        """Devuelve la campaña asociada a una palabra clave"""
        return db.query(Campaign).filter(Campaign.nombre_clave == keyword).first()
