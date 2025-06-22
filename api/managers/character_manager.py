from api.crud import character as crud_character
from api.schemas.character import CharacterCreate
from sqlalchemy.orm import Session
from api.models.character import Character

class CharacterManager:
    @staticmethod
    def create(db: Session, character: CharacterCreate):
        return crud_character.create(db, character)

    @staticmethod
    def get(db: Session, character_id: int):
        return crud_character.get(db, character_id)

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        return crud_character.list(db, skip, limit)

    @staticmethod
    def delete(db: Session, character_id: int):
        return crud_character.delete(db, character_id)

    @staticmethod
    def update(db: Session, character_id: int, character_data: dict):
        return crud_character.update(db, character_id, character_data)

    @staticmethod
    def get_model():
        return Character
