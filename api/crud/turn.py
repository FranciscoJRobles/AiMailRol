from sqlalchemy.orm import Session
from api.models.turn import Turn
from api.schemas.turn import TurnCreate, TurnUpdate
from typing import List, Optional
from datetime import datetime, timezone

def get_turn(db: Session, turn_id: int) -> Optional[Turn]:
    return db.query(Turn).filter(Turn.id == turn_id).first()

def get_turns(db: Session, skip: int = 0, limit: int = 100) -> List[Turn]:
    return db.query(Turn).offset(skip).limit(limit).all()

def create_turn(db: Session, turn: TurnCreate) -> Turn:
    db_turn = Turn(**turn.model_dump())
    db.add(db_turn)
    db.commit()
    db.refresh(db_turn)
    return db_turn

def update_turn(db: Session, turn_id: int, turn_update: TurnUpdate) -> Optional[Turn]:
    db_turn = get_turn(db, turn_id)
    if not db_turn:
        return None
    for field, value in turn_update.model_dump(exclude_unset=True).items():
        setattr(db_turn, field, value)
    db.commit()
    db.refresh(db_turn)
    return db_turn

def delete_turn(db: Session, turn_id: int) -> bool:
    db_turn = get_turn(db, turn_id)
    if not db_turn:
        return False
    db.delete(db_turn)
    db.commit()
    return True
