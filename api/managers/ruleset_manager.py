from sqlalchemy.orm import Session
from api.models.ruleset import Ruleset
from api.schemas.ruleset import RulesetCreate, RulesetUpdate
from typing import List, Optional
from fastapi import HTTPException

class RulesetManager:
    @staticmethod
    def get_ruleset(db: Session, ruleset_id: int) -> Optional[Ruleset]:
        """Obtiene un ruleset por ID"""
        return db.query(Ruleset).filter(Ruleset.id == ruleset_id).first()

    @staticmethod
    def get_rulesets(db: Session, skip: int = 0, limit: int = 100) -> List[Ruleset]:
        """Lista todos los rulesets con paginación"""
        return db.query(Ruleset).offset(skip).limit(limit).all()

    @staticmethod
    def create_ruleset(db: Session, ruleset: RulesetCreate) -> Ruleset:
        """Crea un nuevo ruleset"""
        db_ruleset = Ruleset(**ruleset.model_dump())
        db.add(db_ruleset)
        db.commit()
        db.refresh(db_ruleset)
        return db_ruleset

    @staticmethod
    def update_ruleset(db: Session, ruleset_id: int, ruleset_update: RulesetUpdate) -> Optional[Ruleset]:
        """Actualiza un ruleset"""
        db_ruleset = RulesetManager.get_ruleset(db, ruleset_id)
        if not db_ruleset:
            return None
        for field, value in ruleset_update.model_dump(exclude_unset=True).items():
            setattr(db_ruleset, field, value)
        db.commit()
        db.refresh(db_ruleset)
        return db_ruleset

    @staticmethod
    def delete_ruleset(db: Session, ruleset_id: int) -> bool:
        """Elimina un ruleset"""
        db_ruleset = RulesetManager.get_ruleset(db, ruleset_id)
        if not db_ruleset:
            return False
        db.delete(db_ruleset)
        db.commit()
        return True

    @staticmethod
    def get_ruleset_by_campaign_id(db: Session, campaign_id: int) -> Optional[Ruleset]:
        """Obtiene un ruleset asociado a un campaign_id"""
        return db.query(Ruleset).filter(Ruleset.campaign_id == campaign_id).first()

