from sqlalchemy.orm import Session
from api.models.story import Story
from api.models.character import Character
from api.schemas.story import StoryCreate, StoryUpdate
from typing import List, Optional
from datetime import datetime, timezone

class StoryManager:
    @staticmethod
    def get_story(db: Session, story_id: int) -> Optional[Story]:
        """Obtiene una historia por ID"""
        return db.query(Story).filter(Story.id == story_id).first()

    @staticmethod
    def get_story_by_id(db: Session, story_id: int):
        """Devuelve la historia correspondiente al id"""
        return db.query(Story).filter(Story.id == story_id).first()

    @staticmethod
    def get_stories(db: Session, skip: int = 0, limit: int = 100) -> List[Story]:
        """Lista todas las historias con paginación"""
        return db.query(Story).offset(skip).limit(limit).all()

    @staticmethod
    def create_story(db: Session, story: StoryCreate) -> Story:
        """Crea una nueva historia"""
        db_story = Story(**story.model_dump())
        db.add(db_story)
        db.commit()
        db.refresh(db_story)
        return db_story

    @staticmethod
    def update_story(db: Session, story_id: int, story_update: StoryUpdate) -> Optional[Story]:
        """Actualiza una historia"""
        db_story = StoryManager.get_story(db, story_id)
        if not db_story:
            return None
        for field, value in story_update.model_dump(exclude_unset=True).items():
            if field == "character_ids":
                characters = db.query(Character).filter(Character.id.in_(value)).all()
                if len(characters) != len(value):
                    raise ValueError("Uno o más character_ids no existen")
                db_story.characters = characters
            else:
                setattr(db_story, field, value)
        db_story.fecha_actualizacion = datetime.now(tz=timezone.utc)
        db.commit()
        db.refresh(db_story)
        return db_story

    @staticmethod
    def delete_story(db: Session, story_id: int) -> bool:
        """Elimina una historia"""
        db_story = StoryManager.get_story(db, story_id)
        if not db_story:
            return False
        db.delete(db_story)
        db.commit()
        return True

    @staticmethod
    def get_active_story_by_keyword(db: Session, keyword: str, campaign_id: int) -> Optional[Story]:
        """Devuelve la historia activa asociada a una palabra clave y campaña específica"""
        return db.query(Story).filter(
            Story.nombre_clave == keyword,
            Story.campaign_id == campaign_id,
            Story.activa == True
        ).first()
