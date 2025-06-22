from sqlalchemy.orm import Session
from api.schemas.turn import TurnCreate, TurnUpdate
from api.crud import turn as crud_turn
from typing import List, Optional
from api.models.turn import Turn

class TurnManager:
    @staticmethod
    def get_turn(db: Session, turn_id: int) -> Optional[Turn]:
        return crud_turn.get_turn(db, turn_id)

    @staticmethod
    def get_turns(db: Session, skip: int = 0, limit: int = 100) -> List[Turn]:
        return crud_turn.get_turns(db, skip, limit)

    @staticmethod
    def create_turn(db: Session, turn: TurnCreate) -> Turn:
        return crud_turn.create_turn(db, turn)

    @staticmethod
    def update_turn(db: Session, turn_id: int, turn_update: TurnUpdate) -> Optional[Turn]:
        return crud_turn.update_turn(db, turn_id, turn_update)

    @staticmethod
    def delete_turn(db: Session, turn_id: int) -> bool:
        return crud_turn.delete_turn(db, turn_id)
