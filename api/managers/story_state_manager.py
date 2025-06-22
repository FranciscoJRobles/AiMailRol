from sqlalchemy.orm import Session
from api.schemas.story_state import StoryStateCreate, StoryStateUpdate
from api.crud import story_state as crud_story_state
from typing import List, Optional
from api.models.story_state import StoryState

class StoryStateManager:
    @staticmethod
    def get_story_state(db: Session, story_state_id: int) -> Optional[StoryState]:
        return crud_story_state.get_story_state(db, story_state_id)

    @staticmethod
    def get_story_states(db: Session, skip: int = 0, limit: int = 100) -> List[StoryState]:
        return crud_story_state.get_story_states(db, skip, limit)

    @staticmethod
    def create_story_state(db: Session, story_state: StoryStateCreate) -> StoryState:
        return crud_story_state.create_story_state(db, story_state)

    @staticmethod
    def update_story_state(db: Session, story_state_id: int, story_state_update: StoryStateUpdate) -> Optional[StoryState]:
        return crud_story_state.update_story_state(db, story_state_id, story_state_update)

    @staticmethod
    def delete_story_state(db: Session, story_state_id: int) -> bool:
        return crud_story_state.delete_story_state(db, story_state_id)
