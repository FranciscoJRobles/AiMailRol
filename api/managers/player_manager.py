from api.crud import player as crud_player
from api.schemas.player import PlayerCreate, PlayerUpdate
from sqlalchemy.orm import Session

class PlayerManager:
    @staticmethod
    def create(db: Session, player: PlayerCreate):
        return crud_player.create(db, player)

    @staticmethod
    def get(db: Session, player_id: int):
        return crud_player.get(db, player_id)

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        return crud_player.list(db, skip, limit)

    @staticmethod
    def delete(db: Session, player_id: int):
        return crud_player.delete(db, player_id)

    @staticmethod
    def update(db: Session, player_id: int, player_data: dict):
        return crud_player.update(db, player_id, player_data)
