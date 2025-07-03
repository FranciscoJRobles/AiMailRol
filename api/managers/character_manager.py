from sqlalchemy.orm import Session
from api.models.character import Character
from api.models.associations import campaign_characters, story_characters
from api.schemas.character import CharacterCreate, CharacterUpdate
from fastapi import HTTPException, status

class CharacterManager:
    @staticmethod
    def create(db: Session, character: CharacterCreate):
        """Crea un nuevo personaje"""
        db_character = Character(**character.model_dump())
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character

    @staticmethod
    def get(db: Session, character_id: int):
        """Obtiene un personaje por ID"""
        character = db.query(Character).filter(Character.id == character_id).first()
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        return character

    @staticmethod
    def list(db: Session, skip: int = 0, limit: int = 100):
        """Lista todos los personajes con paginación"""
        return db.query(Character).offset(skip).limit(limit).all()

    @staticmethod
    def delete(db: Session, character_id: int):
        """Elimina un personaje"""
        character = CharacterManager.get(db, character_id)
        db.delete(character)
        db.commit()
        return character

    @staticmethod
    def update(db: Session, character_id: int, character_data: CharacterUpdate):
        """Actualiza un personaje"""
        character = CharacterManager.get(db, character_id)
        for key, value in character_data.model_dump(exclude_unset=True).items():
            setattr(character, key, value)
        db.commit()
        db.refresh(character)
        return character

    @staticmethod
    def get_character_id_by_player_and_campaign(db: Session, player_id: int, campaign_id: int):
        """Devuelve el character_id del personaje de un jugador en una campaña concreta"""
        character = db.query(Character).filter(
            Character.player_id == player_id,
            Character.campaigns.any(id=campaign_id)
        ).first()
        return character.id if character else None

    @staticmethod
    def get_model():
        """Devuelve el modelo Character"""
        return Character

    @staticmethod
    def get_characters_by_story_id(db: Session, story_id: int):
        """Devuelve una lista de instancias de Character asociadas a una historia"""
        return db.query(Character).join(story_characters).filter(story_characters.c.story_id == story_id).all()