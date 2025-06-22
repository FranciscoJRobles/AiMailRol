from sqlalchemy.orm import Session
from api.schemas.ruleset import RulesetCreate, RulesetUpdate
from api.crud import ruleset as crud_ruleset
from typing import List, Optional
from api.models.ruleset import Ruleset

class RulesetManager:
    @staticmethod
    def get_ruleset(db: Session, ruleset_id: int) -> Optional[Ruleset]:
        return crud_ruleset.get_ruleset(db, ruleset_id)

    @staticmethod
    def get_rulesets(db: Session, skip: int = 0, limit: int = 100) -> List[Ruleset]:
        return crud_ruleset.get_rulesets(db, skip, limit)

    @staticmethod
    def create_ruleset(db: Session, ruleset: RulesetCreate) -> Ruleset:
        return crud_ruleset.create_ruleset(db, ruleset)

    @staticmethod
    def update_ruleset(db: Session, ruleset_id: int, ruleset_update: RulesetUpdate) -> Optional[Ruleset]:
        return crud_ruleset.update_ruleset(db, ruleset_id, ruleset_update)

    @staticmethod
    def delete_ruleset(db: Session, ruleset_id: int) -> bool:
        return crud_ruleset.delete_ruleset(db, ruleset_id)
