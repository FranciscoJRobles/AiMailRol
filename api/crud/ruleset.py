from sqlalchemy.orm import Session
from api.models.ruleset import Ruleset
from api.schemas.ruleset import RulesetCreate, RulesetUpdate
from typing import List, Optional

def get_ruleset(db: Session, ruleset_id: int) -> Optional[Ruleset]:
    return db.query(Ruleset).filter(Ruleset.id == ruleset_id).first()

def get_rulesets(db: Session, skip: int = 0, limit: int = 100) -> List[Ruleset]:
    return db.query(Ruleset).offset(skip).limit(limit).all()

def create_ruleset(db: Session, ruleset: RulesetCreate) -> Ruleset:
    db_ruleset = Ruleset(**ruleset.model_dump())
    db.add(db_ruleset)
    db.commit()
    db.refresh(db_ruleset)
    return db_ruleset

def update_ruleset(db: Session, ruleset_id: int, ruleset_update: RulesetUpdate) -> Optional[Ruleset]:
    db_ruleset = get_ruleset(db, ruleset_id)
    if not db_ruleset:
        return None
    for field, value in ruleset_update.model_dump(exclude_unset=True).items():
        setattr(db_ruleset, field, value)
    db.commit()
    db.refresh(db_ruleset)
    return db_ruleset

def delete_ruleset(db: Session, ruleset_id: int) -> bool:
    db_ruleset = get_ruleset(db, ruleset_id)
    if not db_ruleset:
        return False
    db.delete(db_ruleset)
    db.commit()
    return True
