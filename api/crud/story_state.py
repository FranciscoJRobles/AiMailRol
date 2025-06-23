from sqlalchemy.orm import Session
from api.models.story_state import StoryState
from api.models.character import Character
from api.schemas.story_state import StoryStateCreate, StoryStateUpdate
from typing import List, Optional
from datetime import datetime, timezone

def get_story_state(db: Session, story_state_id: int) -> Optional[StoryState]:
    return db.query(StoryState).filter(StoryState.id == story_state_id).first()

def get_story_states(db: Session, skip: int = 0, limit: int = 100) -> List[StoryState]:
    return db.query(StoryState).offset(skip).limit(limit).all()

def create_story_state(db: Session, story_state: StoryStateCreate) -> StoryState:
    db_story_state = StoryState(**story_state.model_dump())
    db.add(db_story_state)
    db.commit()
    db.refresh(db_story_state)
    return db_story_state

def update_story_state(db: Session, story_state_id: int, story_state_update: StoryStateUpdate) -> Optional[StoryState]:
    db_story_state = get_story_state(db, story_state_id)
    if not db_story_state:
        return None
    for field, value in story_state_update.model_dump(exclude_unset=True).items():
        if field == "character_ids":
            characters = db.query(Character).filter(Character.id.in_(value)).all()
            if len(characters) != len(value):
                raise ValueError("Uno o más character_ids no existen")
            db_story_state.characters = characters
        else:
            setattr(db_story_state, field, value)
    db_story_state.fecha_actualizacion = datetime.now(tz=timezone.utc)
    db.commit()
    db.refresh(db_story_state)
    return db_story_state

def delete_story_state(db: Session, story_state_id: int) -> bool:
    db_story_state = get_story_state(db, story_state_id)
    if not db_story_state:
        return False
    db.delete(db_story_state)
    db.commit()
    return True
