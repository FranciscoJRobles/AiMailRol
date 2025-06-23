from sqlalchemy.orm import Session
from api.models.campaign import Campaign
from api.models.character import Character
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
